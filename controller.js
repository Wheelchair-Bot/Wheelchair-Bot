/**
 * Controller UI Manager
 * Handles user interface interactions and control commands
 */

class ControllerUI {
    constructor(webrtcManager) {
        this.webrtc = webrtcManager;
        this.currentSpeed = 50;
        this.activeDirection = null;
        
        // Get DOM elements
        this.connectBtn = document.getElementById('connectBtn');
        this.disconnectBtn = document.getElementById('disconnectBtn');
        this.serverUrlInput = document.getElementById('serverUrl');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedValue = document.getElementById('speedValue');
        
        // Control buttons
        this.controlButtons = {
            forward: document.getElementById('btn-forward'),
            backward: document.getElementById('btn-backward'),
            left: document.getElementById('btn-left'),
            right: document.getElementById('btn-right'),
            stop: document.getElementById('btn-stop')
        };
        
        this.initializeEventListeners();
        this.setupWebRTCCallbacks();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Connection buttons
        this.connectBtn.addEventListener('click', () => this.handleConnect());
        this.disconnectBtn.addEventListener('click', () => this.handleDisconnect());
        
        // Speed slider
        this.speedSlider.addEventListener('input', (e) => {
            this.currentSpeed = parseInt(e.target.value);
            this.speedValue.textContent = `${this.currentSpeed}%`;
        });
        
        // Control buttons - mouse events
        Object.entries(this.controlButtons).forEach(([direction, button]) => {
            button.addEventListener('mousedown', () => this.handleControlPress(direction));
            button.addEventListener('mouseup', () => this.handleControlRelease(direction));
            button.addEventListener('mouseleave', () => this.handleControlRelease(direction));
            
            // Touch events for mobile
            button.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.handleControlPress(direction);
            });
            button.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.handleControlRelease(direction);
            });
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        
        // Enter key in server URL input
        this.serverUrlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.connectBtn.disabled) {
                this.handleConnect();
            }
        });
    }

    /**
     * Setup WebRTC manager callbacks
     */
    setupWebRTCCallbacks() {
        this.webrtc.onConnectionStateChange = (state) => {
            this.updateConnectionStatus(state);
        };
        
        this.webrtc.onDataChannelReady = () => {
            console.log('Data channel ready for commands');
        };
    }

    /**
     * Handle connect button click
     */
    async handleConnect() {
        const serverUrl = this.serverUrlInput.value.trim();
        
        if (!serverUrl) {
            alert('Please enter a server URL');
            return;
        }
        
        this.connectBtn.disabled = true;
        this.serverUrlInput.disabled = true;
        
        try {
            await this.webrtc.connect(serverUrl);
            this.disconnectBtn.disabled = false;
        } catch (error) {
            console.error('Connection failed:', error);
            alert('Failed to connect: ' + error.message);
            this.connectBtn.disabled = false;
            this.serverUrlInput.disabled = false;
        }
    }

    /**
     * Handle disconnect button click
     */
    handleDisconnect() {
        this.webrtc.disconnect();
        this.connectBtn.disabled = false;
        this.disconnectBtn.disabled = true;
        this.serverUrlInput.disabled = false;
    }

    /**
     * Handle control button press
     */
    handleControlPress(direction) {
        if (!this.webrtc.isReady()) {
            console.warn('WebRTC not ready');
            return;
        }
        
        this.activeDirection = direction;
        this.controlButtons[direction].classList.add('active');
        this.sendMovementCommand(direction);
    }

    /**
     * Handle control button release
     */
    handleControlRelease(direction) {
        if (this.activeDirection === direction) {
            this.activeDirection = null;
            this.controlButtons[direction].classList.remove('active');
            this.sendMovementCommand('stop');
        }
    }

    /**
     * Handle keyboard press
     */
    handleKeyDown(e) {
        // Ignore if typing in input field
        if (e.target.tagName === 'INPUT') {
            return;
        }
        
        const keyMap = {
            'ArrowUp': 'forward',
            'w': 'forward',
            'W': 'forward',
            'ArrowDown': 'backward',
            's': 'backward',
            'S': 'backward',
            'ArrowLeft': 'left',
            'a': 'left',
            'A': 'left',
            'ArrowRight': 'right',
            'd': 'right',
            'D': 'right',
            ' ': 'stop',
            'Escape': 'stop'
        };
        
        const direction = keyMap[e.key];
        
        if (direction && this.activeDirection !== direction) {
            e.preventDefault();
            this.handleControlPress(direction);
        }
    }

    /**
     * Handle keyboard release
     */
    handleKeyUp(e) {
        // Ignore if typing in input field
        if (e.target.tagName === 'INPUT') {
            return;
        }
        
        const keyMap = {
            'ArrowUp': 'forward',
            'w': 'forward',
            'W': 'forward',
            'ArrowDown': 'backward',
            's': 'backward',
            'S': 'backward',
            'ArrowLeft': 'left',
            'a': 'left',
            'A': 'left',
            'ArrowRight': 'right',
            'd': 'right',
            'D': 'right',
            ' ': 'stop',
            'Escape': 'stop'
        };
        
        const direction = keyMap[e.key];
        
        if (direction) {
            e.preventDefault();
            this.handleControlRelease(direction);
        }
    }

    /**
     * Send movement command through WebRTC
     */
    sendMovementCommand(direction) {
        const command = {
            type: 'movement',
            direction: direction,
            speed: this.currentSpeed,
            timestamp: Date.now()
        };
        
        const success = this.webrtc.sendCommand(command);
        
        if (success) {
            console.log('Sent command:', command);
        } else {
            console.warn('Failed to send command');
        }
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(state) {
        const statusMap = {
            'connecting': {
                text: 'Connecting...',
                class: 'connecting'
            },
            'connected': {
                text: 'Connected',
                class: 'connected'
            },
            'disconnected': {
                text: 'Disconnected',
                class: ''
            },
            'failed': {
                text: 'Connection Failed',
                class: ''
            },
            'error': {
                text: 'Error',
                class: ''
            }
        };
        
        const status = statusMap[state] || statusMap.disconnected;
        
        this.statusText.textContent = status.text;
        this.statusIndicator.className = 'status-indicator ' + status.class;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const webrtcManager = new WebRTCManager();
    const controllerUI = new ControllerUI(webrtcManager);
    
    console.log('Wheelchair Bot Controller initialized');
    console.log('Keyboard controls: W/↑ = Forward, S/↓ = Backward, A/← = Left, D/→ = Right, Space/Esc = Stop');
});
