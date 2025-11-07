/**
 * WebRTC Manager
 * Handles WebRTC peer connection, signaling, and data channels
 */

class WebRTCManager {
    constructor() {
        this.peerConnection = null;
        this.dataChannel = null;
        this.websocket = null;
        this.remoteVideo = document.getElementById('remoteVideo');
        this.videoOverlay = document.getElementById('videoOverlay');
        
        // State tracking
        this.isConnected = false;
        this.isConnecting = false;
        
        // Configuration
        this.config = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };
        
        // Callbacks
        this.onConnectionStateChange = null;
        this.onDataChannelReady = null;
        this.onDataChannelMessage = null;
    }

    /**
     * Connect to the signaling server
     */
    async connect(serverUrl) {
        if (this.isConnected || this.isConnecting) {
            console.warn('Already connected or connecting');
            return;
        }

        this.isConnecting = true;
        this.updateConnectionState('connecting');

        try {
            // Connect to WebSocket signaling server
            this.websocket = new WebSocket(serverUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.initializePeerConnection();
            };

            this.websocket.onmessage = async (event) => {
                await this.handleSignalingMessage(JSON.parse(event.data));
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionState('error');
            };

            this.websocket.onclose = () => {
                console.log('WebSocket closed');
                this.disconnect();
            };

        } catch (error) {
            console.error('Connection error:', error);
            this.isConnecting = false;
            this.updateConnectionState('error');
            throw error;
        }
    }

    /**
     * Initialize WebRTC peer connection
     */
    initializePeerConnection() {
        this.peerConnection = new RTCPeerConnection(this.config);

        // Handle ICE candidates
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignalingMessage({
                    type: 'ice-candidate',
                    candidate: event.candidate
                });
            }
        };

        // Handle connection state changes
        this.peerConnection.onconnectionstatechange = () => {
            console.log('Connection state:', this.peerConnection.connectionState);
            this.updateConnectionState(this.peerConnection.connectionState);
            
            if (this.peerConnection.connectionState === 'connected') {
                this.isConnected = true;
                this.isConnecting = false;
            } else if (this.peerConnection.connectionState === 'failed' || 
                       this.peerConnection.connectionState === 'disconnected') {
                this.isConnected = false;
                this.isConnecting = false;
            }
        };

        // Handle ICE connection state changes
        this.peerConnection.oniceconnectionstatechange = () => {
            console.log('ICE connection state:', this.peerConnection.iceConnectionState);
            this.updateUIState('iceState', this.peerConnection.iceConnectionState);
        };

        // Handle signaling state changes
        this.peerConnection.onsignalingstatechange = () => {
            console.log('Signaling state:', this.peerConnection.signalingState);
            this.updateUIState('signalingState', this.peerConnection.signalingState);
        };

        // Handle incoming media streams
        this.peerConnection.ontrack = (event) => {
            console.log('Received remote track:', event.track.kind);
            if (event.streams && event.streams[0]) {
                this.remoteVideo.srcObject = event.streams[0];
                this.videoOverlay.classList.add('hidden');
            }
        };

        // Create data channel for control commands
        this.createDataChannel();

        // Create and send offer
        this.createOffer();
    }

    /**
     * Create data channel for sending control commands
     */
    createDataChannel() {
        this.dataChannel = this.peerConnection.createDataChannel('control', {
            ordered: true
        });

        this.dataChannel.onopen = () => {
            console.log('Data channel opened');
            this.updateUIState('dataChannelState', 'open');
            if (this.onDataChannelReady) {
                this.onDataChannelReady();
            }
        };

        this.dataChannel.onclose = () => {
            console.log('Data channel closed');
            this.updateUIState('dataChannelState', 'closed');
        };

        this.dataChannel.onerror = (error) => {
            console.error('Data channel error:', error);
            this.updateUIState('dataChannelState', 'error');
        };

        this.dataChannel.onmessage = (event) => {
            if (this.onDataChannelMessage) {
                this.onDataChannelMessage(event.data);
            }
        };
    }

    /**
     * Create and send WebRTC offer
     */
    async createOffer() {
        try {
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            this.sendSignalingMessage({
                type: 'offer',
                sdp: offer
            });
        } catch (error) {
            console.error('Error creating offer:', error);
        }
    }

    /**
     * Handle incoming signaling messages
     */
    async handleSignalingMessage(message) {
        try {
            switch (message.type) {
                case 'answer':
                    await this.peerConnection.setRemoteDescription(
                        new RTCSessionDescription(message.sdp)
                    );
                    break;

                case 'ice-candidate':
                    if (message.candidate) {
                        await this.peerConnection.addIceCandidate(
                            new RTCIceCandidate(message.candidate)
                        );
                    }
                    break;

                case 'offer':
                    await this.peerConnection.setRemoteDescription(
                        new RTCSessionDescription(message.sdp)
                    );
                    const answer = await this.peerConnection.createAnswer();
                    await this.peerConnection.setLocalDescription(answer);
                    this.sendSignalingMessage({
                        type: 'answer',
                        sdp: answer
                    });
                    break;

                default:
                    console.warn('Unknown message type:', message.type);
            }
        } catch (error) {
            console.error('Error handling signaling message:', error);
        }
    }

    /**
     * Send message through signaling channel
     */
    sendSignalingMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket not connected');
        }
    }

    /**
     * Send control command through data channel
     */
    sendCommand(command) {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            this.dataChannel.send(JSON.stringify(command));
            return true;
        } else {
            console.warn('Data channel not ready');
            return false;
        }
    }

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        console.log('Disconnecting...');

        if (this.dataChannel) {
            this.dataChannel.close();
            this.dataChannel = null;
        }

        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }

        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }

        if (this.remoteVideo.srcObject) {
            this.remoteVideo.srcObject.getTracks().forEach(track => track.stop());
            this.remoteVideo.srcObject = null;
        }

        this.videoOverlay.classList.remove('hidden');
        this.isConnected = false;
        this.isConnecting = false;
        
        this.updateConnectionState('disconnected');
        this.updateUIState('iceState', '-');
        this.updateUIState('signalingState', '-');
        this.updateUIState('dataChannelState', '-');
    }

    /**
     * Update connection state and trigger callback
     */
    updateConnectionState(state) {
        if (this.onConnectionStateChange) {
            this.onConnectionStateChange(state);
        }
    }

    /**
     * Update UI state element
     */
    updateUIState(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Check if ready to send commands
     */
    isReady() {
        return this.dataChannel && this.dataChannel.readyState === 'open';
    }
}
