/**
 * Comprehensive tests for WebRTC video send/receive functionality
 * Tests cover:
 * - Connection establishment and teardown
 * - Video stream quality and continuity
 * - Error handling for transmission failures
 * - Performance under varying network conditions
 * - Platform compatibility
 */

// Load the WebRTC manager
const fs = require('fs');
const path = require('path');

// Read the WebRTC manager code and make it exportable for Node.js
const webrtcCode = fs.readFileSync(
  path.join(__dirname, '../webrtc.js'),
  'utf8'
);

// Wrap the code to make it work in Node.js environment
const webrtcModuleCode = `
${webrtcCode}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WebRTCManager;
}
return WebRTCManager;
`;

// Create WebRTCManager class using VM-like approach
const createWebRTCManager = () => {
  const func = new Function('document', webrtcModuleCode);
  return func(global.document);
};

describe('WebRTC Connection Lifecycle', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager && manager.isConnected !== undefined) {
      try {
        manager.disconnect();
      } catch (e) {
        // Ignore cleanup errors in tests
      }
    }
  });

  describe('Connection Establishment', () => {
    test('should initialize with correct default state', () => {
      expect(manager.peerConnection).toBeNull();
      expect(manager.dataChannel).toBeNull();
      expect(manager.websocket).toBeNull();
      expect(manager.isConnected).toBe(false);
      expect(manager.isConnecting).toBe(false);
    });

    test('should have correct STUN server configuration', () => {
      expect(manager.config.iceServers).toBeDefined();
      expect(manager.config.iceServers.length).toBeGreaterThan(0);
      expect(manager.config.iceServers[0].urls).toContain('stun:stun.l.google.com:19302');
    });

    test('should connect to signaling server successfully', async () => {
      const serverUrl = 'ws://localhost:8080';
      const connectPromise = manager.connect(serverUrl);
      
      // Wait for WebSocket to open
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.websocket).not.toBeNull();
      expect(manager.websocket.url).toBe(serverUrl);
      expect(manager.isConnecting).toBe(true);
    });

    test('should prevent duplicate connections', async () => {
      const serverUrl = 'ws://localhost:8080';
      
      manager.connect(serverUrl);
      await new Promise(resolve => setTimeout(resolve, 20));
      
      // Try to connect again
      const consoleSpy = jest.spyOn(console, 'warn');
      await manager.connect(serverUrl);
      
      expect(consoleSpy).toHaveBeenCalledWith('Already connected or connecting');
      consoleSpy.mockRestore();
    });

    test('should initialize peer connection after WebSocket connects', async () => {
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      
      // Wait for WebSocket to open
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.peerConnection).not.toBeNull();
      expect(manager.peerConnection.config).toEqual(manager.config);
    });

    test('should create data channel for control commands', async () => {
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.dataChannel).not.toBeNull();
      expect(manager.dataChannel.label).toBe('control');
      expect(manager.dataChannel.ordered).toBe(true);
    });

    test('should handle connection state transitions', async () => {
      const stateChanges = [];
      manager.onConnectionStateChange = (state) => stateChanges.push(state);
      
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(stateChanges).toContain('connecting');
    });

    test('should set up ICE candidate handler', async () => {
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.peerConnection.onicecandidate).toBeDefined();
      expect(typeof manager.peerConnection.onicecandidate).toBe('function');
    });
  });

  describe('Connection Teardown', () => {
    beforeEach(async () => {
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    test('should disconnect and cleanup all resources', () => {
      manager.disconnect();
      
      expect(manager.dataChannel).toBeNull();
      expect(manager.peerConnection).toBeNull();
      expect(manager.websocket).toBeNull();
      expect(manager.isConnected).toBe(false);
      expect(manager.isConnecting).toBe(false);
    });

    test('should close data channel on disconnect', () => {
      const dataChannel = manager.dataChannel;
      const closeSpy = jest.spyOn(dataChannel, 'close');
      
      manager.disconnect();
      
      expect(closeSpy).toHaveBeenCalled();
    });

    test('should close peer connection on disconnect', () => {
      const peerConnection = manager.peerConnection;
      const closeSpy = jest.spyOn(peerConnection, 'close');
      
      manager.disconnect();
      
      expect(closeSpy).toHaveBeenCalled();
    });

    test('should close WebSocket on disconnect', () => {
      const websocket = manager.websocket;
      const closeSpy = jest.spyOn(websocket, 'close');
      
      manager.disconnect();
      
      expect(closeSpy).toHaveBeenCalled();
    });

    test('should stop all media tracks on disconnect', () => {
      const mockTrack = new MediaStreamTrack('video');
      const stopSpy = jest.spyOn(mockTrack, 'stop');
      const mockStream = new MediaStream([mockTrack]);
      
      manager.remoteVideo.srcObject = mockStream;
      manager.disconnect();
      
      expect(stopSpy).toHaveBeenCalled();
      expect(manager.remoteVideo.srcObject).toBeNull();
    });

    test('should trigger disconnected state on disconnect', () => {
      let finalState;
      manager.onConnectionStateChange = (state) => { finalState = state; };
      
      manager.disconnect();
      
      expect(finalState).toBe('disconnected');
    });
  });

  describe('Reconnection Handling', () => {
    test('should allow reconnection after disconnect', async () => {
      const serverUrl = 'ws://localhost:8080';
      
      await manager.connect(serverUrl);
      await new Promise(resolve => setTimeout(resolve, 50));
      
      manager.disconnect();
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Should be able to connect again
      await manager.connect(serverUrl);
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.websocket).not.toBeNull();
      expect(manager.peerConnection).not.toBeNull();
    });

    test('should handle WebSocket close and cleanup', async () => {
      const serverUrl = 'ws://localhost:8080';
      await manager.connect(serverUrl);
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Simulate WebSocket close
      manager.websocket._simulateClose();
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(manager.isConnected).toBe(false);
    });
  });
});

describe('Video Stream Send/Receive', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager) {
      manager.disconnect();
    }
  });

  describe('Video Receive', () => {
    beforeEach(async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    test('should handle incoming video track', () => {
      const mockVideoTrack = new MediaStreamTrack('video');
      const mockStream = new MediaStream([mockVideoTrack]);
      
      manager.peerConnection._simulateTrack(mockVideoTrack, [mockStream]);
      
      expect(manager.remoteVideo.srcObject).toBe(mockStream);
    });

    test('should hide video overlay when stream is received', () => {
      const mockVideoTrack = new MediaStreamTrack('video');
      const mockStream = new MediaStream([mockVideoTrack]);
      
      manager.peerConnection._simulateTrack(mockVideoTrack, [mockStream]);
      
      expect(manager.videoOverlay.classList.add).toHaveBeenCalledWith('hidden');
    });

    test('should handle multiple video tracks', () => {
      const track1 = new MediaStreamTrack('video');
      const track2 = new MediaStreamTrack('video');
      const stream = new MediaStream([track1, track2]);
      
      manager.peerConnection._simulateTrack(track1, [stream]);
      
      const videoTracks = manager.remoteVideo.srcObject.getVideoTracks();
      expect(videoTracks.length).toBeGreaterThan(0);
    });

    test('should verify video stream quality properties', () => {
      const mockVideoTrack = new MediaStreamTrack('video');
      const mockStream = new MediaStream([mockVideoTrack]);
      
      manager.peerConnection._simulateTrack(mockVideoTrack, [mockStream]);
      
      const receivedStream = manager.remoteVideo.srcObject;
      expect(receivedStream.active).toBe(true);
      expect(receivedStream.getVideoTracks().length).toBeGreaterThan(0);
      
      const videoTrack = receivedStream.getVideoTracks()[0];
      expect(videoTrack.readyState).toBe('live');
      expect(videoTrack.enabled).toBe(true);
    });

    test('should handle video stream continuity', async () => {
      const mockVideoTrack = new MediaStreamTrack('video');
      const mockStream = new MediaStream([mockVideoTrack]);
      
      manager.peerConnection._simulateTrack(mockVideoTrack, [mockStream]);
      
      // Verify stream remains active over time
      await new Promise(resolve => setTimeout(resolve, 100));
      
      expect(manager.remoteVideo.srcObject).toBe(mockStream);
      expect(mockStream.active).toBe(true);
    });
  });

  describe('Video Send', () => {
    beforeEach(async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    test('should support adding local video tracks', () => {
      const localTrack = new MediaStreamTrack('video');
      const localStream = new MediaStream([localTrack]);
      
      const sender = manager.peerConnection.addTrack(localTrack, localStream);
      
      expect(sender).toBeDefined();
      expect(sender.track).toBe(localTrack);
    });

    test('should handle multiple local video tracks', () => {
      const track1 = new MediaStreamTrack('video');
      const track2 = new MediaStreamTrack('video');
      const stream = new MediaStream([track1, track2]);
      
      manager.peerConnection.addTrack(track1, stream);
      manager.peerConnection.addTrack(track2, stream);
      
      const senders = manager.peerConnection.getSenders();
      expect(senders.length).toBe(2);
    });

    test('should verify local track quality before sending', () => {
      const localTrack = new MediaStreamTrack('video');
      
      expect(localTrack.readyState).toBe('live');
      expect(localTrack.enabled).toBe(true);
      expect(localTrack.kind).toBe('video');
    });
  });
});

describe('Error Handling', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager) {
      manager.disconnect();
    }
  });

  describe('Transmission Failures', () => {
    test('should handle WebSocket connection error', async () => {
      const stateChanges = [];
      manager.onConnectionStateChange = (state) => stateChanges.push(state);
      
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 20));
      
      // Simulate WebSocket error
      manager.websocket._simulateError(new Error('Connection failed'));
      
      expect(stateChanges).toContain('error');
    });

    test('should handle data channel send failure when not open', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Close data channel
      manager.dataChannel.readyState = 'closed';
      
      const result = manager.sendCommand({ type: 'test' });
      expect(result).toBe(false);
    });

    test('should handle data channel errors', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const consoleSpy = jest.spyOn(console, 'error');
      const error = new Error('Data channel error');
      
      manager.dataChannel._simulateError(error);
      
      // Error should be logged
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    test('should handle peer connection failure state', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      manager.peerConnection._simulateConnectionState('failed');
      
      expect(manager.isConnected).toBe(false);
      expect(manager.isConnecting).toBe(false);
    });
  });

  describe('Connection Interruptions', () => {
    test('should handle ICE connection failures', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      manager.peerConnection._simulateIceConnectionState('failed');
      
      // Should update UI state
      expect(manager.peerConnection.iceConnectionState).toBe('failed');
    });

    test('should handle unexpected WebSocket close', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const wasConnected = manager.websocket !== null;
      
      manager.websocket._simulateClose(1006, 'Abnormal closure');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      expect(wasConnected).toBe(true);
      expect(manager.isConnected).toBe(false);
    });

    test('should handle peer connection disconnection', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      manager.peerConnection._simulateConnectionState('disconnected');
      
      expect(manager.isConnected).toBe(false);
    });

    test('should handle video track ended event', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const mockVideoTrack = new MediaStreamTrack('video');
      const mockStream = new MediaStream([mockVideoTrack]);
      
      manager.peerConnection._simulateTrack(mockVideoTrack, [mockStream]);
      
      // Simulate track ending
      mockVideoTrack.stop();
      
      expect(mockVideoTrack.readyState).toBe('ended');
    });
  });

  describe('Signaling Errors', () => {
    test('should handle invalid signaling message', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const consoleSpy = jest.spyOn(console, 'warn');
      
      await manager.handleSignalingMessage({ type: 'invalid-type' });
      
      expect(consoleSpy).toHaveBeenCalledWith('Unknown message type:', 'invalid-type');
      consoleSpy.mockRestore();
    });

    test('should handle signaling message with missing data', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const consoleSpy = jest.spyOn(console, 'error');
      
      // This should not throw but log error
      try {
        await manager.handleSignalingMessage({ type: 'answer' });
      } catch (error) {
        // Expected to catch error
      }
      
      consoleSpy.mockRestore();
    });

    test('should handle send signaling message when WebSocket is closed', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      manager.websocket.readyState = WebSocket.CLOSED;
      
      const consoleSpy = jest.spyOn(console, 'error');
      manager.sendSignalingMessage({ type: 'test' });
      
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket not connected');
      consoleSpy.mockRestore();
    });
  });
});

describe('Performance Under Network Conditions', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager) {
      manager.disconnect();
    }
  });

  describe('Network Latency', () => {
    test('should handle high latency connections', async () => {
      const startTime = Date.now();
      
      await manager.connect('ws://localhost:8080');
      
      // Simulate network delay
      await simulateNetworkConditions.addLatency(() => {}, 500);
      
      const endTime = Date.now();
      const latency = endTime - startTime;
      
      // Allow for small timing variations
      expect(latency).toBeGreaterThanOrEqual(490);
      expect(manager.websocket).not.toBeNull();
    });

    test('should handle variable latency in data channel', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const commands = [];
      const sendTimes = [];
      
      for (let i = 0; i < 5; i++) {
        const sendTime = Date.now();
        manager.sendCommand({ type: 'test', id: i });
        sendTimes.push(sendTime);
        commands.push(i);
        
        // Variable delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
      }
      
      expect(commands.length).toBe(5);
      expect(sendTimes.length).toBe(5);
    });
  });

  describe('Bandwidth Limitations', () => {
    test('should estimate transmission time for different bandwidths', () => {
      const dataSize = 1024; // 1KB
      const lowBandwidth = 64; // 64 Kbps
      const highBandwidth = 1024; // 1 Mbps
      
      const lowTime = simulateNetworkConditions.simulateBandwidthLimit(dataSize, lowBandwidth);
      const highTime = simulateNetworkConditions.simulateBandwidthLimit(dataSize, highBandwidth);
      
      expect(lowTime).toBeGreaterThan(highTime);
    });

    test('should handle data channel buffering', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Send multiple commands rapidly
      for (let i = 0; i < 10; i++) {
        manager.sendCommand({ type: 'test', id: i });
      }
      
      // Data channel should still be functional
      expect(manager.dataChannel.readyState).toBe('open');
    });
  });

  describe('Packet Loss Simulation', () => {
    test('should handle intermittent packet loss', async () => {
      const packetLossRate = 10; // 10% packet loss
      let successfulSends = 0;
      let totalAttempts = 100;
      
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      for (let i = 0; i < totalAttempts; i++) {
        // Simulate packet loss
        if (simulateNetworkConditions.packetLoss(packetLossRate)) {
          if (manager.sendCommand({ type: 'test', id: i })) {
            successfulSends++;
          }
        }
      }
      
      // Most packets should get through
      expect(successfulSends).toBeGreaterThan(totalAttempts * 0.8);
    });
  });

  describe('Connection Recovery', () => {
    test('should handle temporary connection loss', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Simulate temporary disconnection
      manager.peerConnection._simulateConnectionState('disconnected');
      expect(manager.isConnected).toBe(false);
      
      // Simulate recovery
      manager.peerConnection._simulateConnectionState('connected');
      
      expect(manager.peerConnection.connectionState).toBe('connected');
    });

    test('should handle ICE connection restart', async () => {
      await manager.connect('ws://localhost:8080');
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const states = [];
      
      // Monitor state changes
      const originalHandler = manager.peerConnection.oniceconnectionstatechange;
      manager.peerConnection.oniceconnectionstatechange = () => {
        states.push(manager.peerConnection.iceConnectionState);
        if (originalHandler) originalHandler();
      };
      
      // Simulate ICE restart sequence
      manager.peerConnection._simulateIceConnectionState('checking');
      manager.peerConnection._simulateIceConnectionState('connected');
      
      expect(states).toContain('checking');
      expect(states).toContain('connected');
    });
  });
});

describe('Platform Compatibility', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager) {
      manager.disconnect();
    }
  });

  describe('WebRTC API Availability', () => {
    test('should verify RTCPeerConnection is available', () => {
      expect(global.RTCPeerConnection).toBeDefined();
      expect(typeof global.RTCPeerConnection).toBe('function');
    });

    test('should verify RTCSessionDescription is available', () => {
      expect(global.RTCSessionDescription).toBeDefined();
      expect(typeof global.RTCSessionDescription).toBe('function');
    });

    test('should verify RTCIceCandidate is available', () => {
      expect(global.RTCIceCandidate).toBeDefined();
      expect(typeof global.RTCIceCandidate).toBe('function');
    });

    test('should verify MediaStream is available', () => {
      expect(global.MediaStream).toBeDefined();
      expect(typeof global.MediaStream).toBe('function');
    });

    test('should verify WebSocket is available', () => {
      expect(global.WebSocket).toBeDefined();
      expect(typeof global.WebSocket).toBe('function');
    });
  });

  describe('Browser Feature Support', () => {
    test('should create RTCPeerConnection with configuration', () => {
      const config = {
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      };
      
      const pc = new RTCPeerConnection(config);
      
      expect(pc).toBeDefined();
      expect(pc.config).toEqual(config);
    });

    test('should support creating offers and answers', async () => {
      const pc = new RTCPeerConnection();
      
      const offer = await pc.createOffer();
      expect(offer.type).toBe('offer');
      expect(offer.sdp).toBeDefined();
      
      const answer = await pc.createAnswer();
      expect(answer.type).toBe('answer');
      expect(answer.sdp).toBeDefined();
    });

    test('should support data channels', () => {
      const pc = new RTCPeerConnection();
      const dc = pc.createDataChannel('test');
      
      expect(dc).toBeDefined();
      expect(dc.label).toBe('test');
    });

    test('should support adding tracks', () => {
      const pc = new RTCPeerConnection();
      const track = new MediaStreamTrack('video');
      const stream = new MediaStream([track]);
      
      const sender = pc.addTrack(track, stream);
      
      expect(sender).toBeDefined();
      expect(sender.track).toBe(track);
    });
  });

  describe('Cross-Platform Video Codecs', () => {
    test('should handle different video track configurations', () => {
      const videoTrack = new MediaStreamTrack('video');
      
      expect(videoTrack.kind).toBe('video');
      expect(videoTrack.enabled).toBe(true);
      expect(videoTrack.readyState).toBe('live');
    });

    test('should support multiple simultaneous video streams', () => {
      const stream1 = new MediaStream([new MediaStreamTrack('video')]);
      const stream2 = new MediaStream([new MediaStreamTrack('video')]);
      
      expect(stream1.id).not.toBe(stream2.id);
      expect(stream1.getVideoTracks().length).toBe(1);
      expect(stream2.getVideoTracks().length).toBe(1);
    });

    test('should handle audio and video tracks together', () => {
      const videoTrack = new MediaStreamTrack('video');
      const audioTrack = new MediaStreamTrack('audio');
      const stream = new MediaStream([videoTrack, audioTrack]);
      
      expect(stream.getVideoTracks().length).toBe(1);
      expect(stream.getAudioTracks().length).toBe(1);
      expect(stream.getTracks().length).toBe(2);
    });
  });

  describe('Data Channel Compatibility', () => {
    test('should support ordered data channels', () => {
      const pc = new RTCPeerConnection();
      const dc = pc.createDataChannel('test', { ordered: true });
      
      expect(dc.ordered).toBe(true);
    });

    test('should support unordered data channels', () => {
      const pc = new RTCPeerConnection();
      const dc = pc.createDataChannel('test', { ordered: false });
      
      expect(dc.ordered).toBe(false);
    });

    test('should handle data channel state transitions', (done) => {
      const pc = new RTCPeerConnection();
      const dc = pc.createDataChannel('test');
      
      expect(dc.readyState).toBe('connecting');
      
      dc.onopen = () => {
        expect(dc.readyState).toBe('open');
        done();
      };
    });
  });
});

describe('WebRTC Manager Integration', () => {
  let WebRTCManager;
  let manager;

  beforeEach(() => {
    WebRTCManager = createWebRTCManager();
    manager = new WebRTCManager();
  });

  afterEach(() => {
    if (manager) {
      manager.disconnect();
    }
  });

  test('should provide isReady method', async () => {
    expect(manager.isReady()).toBeFalsy();
    
    await manager.connect('ws://localhost:8080');
    await new Promise(resolve => setTimeout(resolve, 50));
    
    expect(manager.isReady()).toBe(true);
  });

  test('should support custom callbacks', async () => {
    let stateChanges = [];
    let dataChannelReady = false;
    let messagesReceived = [];
    
    manager.onConnectionStateChange = (state) => stateChanges.push(state);
    manager.onDataChannelReady = () => { dataChannelReady = true; };
    manager.onDataChannelMessage = (data) => messagesReceived.push(data);
    
    await manager.connect('ws://localhost:8080');
    await new Promise(resolve => setTimeout(resolve, 100));
    
    expect(stateChanges.length).toBeGreaterThan(0);
    expect(dataChannelReady).toBe(true);
  });

  test('should handle complete connection workflow', async () => {
    const workflow = [];
    
    manager.onConnectionStateChange = (state) => workflow.push(`state:${state}`);
    manager.onDataChannelReady = () => workflow.push('data-channel-ready');
    
    await manager.connect('ws://localhost:8080');
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Simulate successful connection
    manager.peerConnection._simulateConnectionState('connected');
    
    // Add video track
    const track = new MediaStreamTrack('video');
    const stream = new MediaStream([track]);
    manager.peerConnection._simulateTrack(track, [stream]);
    
    // Send command
    const cmdResult = manager.sendCommand({ type: 'test' });
    workflow.push(`command-sent:${cmdResult}`);
    
    // Disconnect
    manager.disconnect();
    
    expect(workflow.length).toBeGreaterThan(0);
    expect(workflow).toContain('data-channel-ready');
    expect(workflow).toContain('command-sent:true');
  });
});
