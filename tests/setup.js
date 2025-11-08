/**
 * Test setup file for WebRTC tests
 * Sets up global mocks and test utilities
 */

// Mock WebRTC APIs that are not available in jsdom
global.RTCPeerConnection = class RTCPeerConnection {
  constructor(config) {
    this.config = config;
    this.localDescription = null;
    this.remoteDescription = null;
    this.connectionState = 'new';
    this.iceConnectionState = 'new';
    this.signalingState = 'stable';
    this.iceGatheringState = 'new';
    this._transceivers = [];
    this._localStreams = [];
    this._remoteStreams = [];
    this._dataChannels = new Map();
    
    // Event handlers
    this.onicecandidate = null;
    this.ontrack = null;
    this.onconnectionstatechange = null;
    this.oniceconnectionstatechange = null;
    this.onsignalingstatechange = null;
    this.ondatachannel = null;
  }

  createOffer(options) {
    return Promise.resolve({
      type: 'offer',
      sdp: 'mock-offer-sdp'
    });
  }

  createAnswer(options) {
    return Promise.resolve({
      type: 'answer',
      sdp: 'mock-answer-sdp'
    });
  }

  setLocalDescription(description) {
    this.localDescription = description;
    this.signalingState = 'have-local-offer';
    if (this.onsignalingstatechange) {
      this.onsignalingstatechange();
    }
    return Promise.resolve();
  }

  setRemoteDescription(description) {
    this.remoteDescription = description;
    this.signalingState = description.type === 'offer' ? 'have-remote-offer' : 'stable';
    if (this.onsignalingstatechange) {
      this.onsignalingstatechange();
    }
    return Promise.resolve();
  }

  addIceCandidate(candidate) {
    return Promise.resolve();
  }

  createDataChannel(label, options = {}) {
    const channel = new MockRTCDataChannel(label, options);
    this._dataChannels.set(label, channel);
    return channel;
  }

  addTrack(track, ...streams) {
    const transceiver = {
      sender: { track },
      receiver: { track: null }
    };
    this._transceivers.push(transceiver);
    return transceiver.sender;
  }

  getSenders() {
    return this._transceivers.map(t => t.sender);
  }

  getReceivers() {
    return this._transceivers.map(t => t.receiver);
  }

  getTransceivers() {
    return this._transceivers;
  }

  close() {
    this.connectionState = 'closed';
    this.iceConnectionState = 'closed';
    if (this.onconnectionstatechange) {
      this.onconnectionstatechange();
    }
    if (this.oniceconnectionstatechange) {
      this.oniceconnectionstatechange();
    }
    
    // Close all data channels
    this._dataChannels.forEach(channel => {
      channel.close();
    });
  }

  // Helper method to simulate connection state changes
  _simulateConnectionState(state) {
    this.connectionState = state;
    if (this.onconnectionstatechange) {
      this.onconnectionstatechange();
    }
  }

  _simulateIceConnectionState(state) {
    this.iceConnectionState = state;
    if (this.oniceconnectionstatechange) {
      this.oniceconnectionstatechange();
    }
  }

  _simulateIceCandidate(candidate) {
    if (this.onicecandidate) {
      this.onicecandidate({ candidate });
    }
  }

  _simulateTrack(track, streams) {
    if (this.ontrack) {
      this.ontrack({ track, streams });
    }
  }
};

global.RTCSessionDescription = class RTCSessionDescription {
  constructor(descriptionInitDict) {
    this.type = descriptionInitDict.type;
    this.sdp = descriptionInitDict.sdp;
  }
};

global.RTCIceCandidate = class RTCIceCandidate {
  constructor(candidateInitDict) {
    Object.assign(this, candidateInitDict);
  }
};

class MockRTCDataChannel {
  constructor(label, options = {}) {
    this.label = label;
    this.ordered = options.ordered !== false;
    this.readyState = 'connecting';
    this.bufferedAmount = 0;
    
    // Event handlers
    this.onopen = null;
    this.onclose = null;
    this.onerror = null;
    this.onmessage = null;
    
    // Simulate opening after a short delay
    setTimeout(() => {
      this.readyState = 'open';
      if (this.onopen) {
        this.onopen();
      }
    }, 10);
  }

  send(data) {
    if (this.readyState !== 'open') {
      throw new Error('DataChannel is not open');
    }
    // Simulate successful send
    return true;
  }

  close() {
    this.readyState = 'closed';
    if (this.onclose) {
      this.onclose();
    }
  }

  // Helper method to simulate receiving a message
  _simulateMessage(data) {
    if (this.onmessage) {
      this.onmessage({ data });
    }
  }

  // Helper method to simulate error
  _simulateError(error) {
    if (this.onerror) {
      this.onerror(error);
    }
  }
}

global.MediaStream = class MediaStream {
  constructor(tracks = []) {
    this.id = Math.random().toString(36).substr(2, 9);
    this.active = true;
    this._tracks = tracks;
  }

  getTracks() {
    return this._tracks;
  }

  getVideoTracks() {
    return this._tracks.filter(t => t.kind === 'video');
  }

  getAudioTracks() {
    return this._tracks.filter(t => t.kind === 'audio');
  }

  addTrack(track) {
    this._tracks.push(track);
  }

  removeTrack(track) {
    const index = this._tracks.indexOf(track);
    if (index > -1) {
      this._tracks.splice(index, 1);
    }
  }
};

global.MediaStreamTrack = class MediaStreamTrack {
  constructor(kind = 'video') {
    this.id = Math.random().toString(36).substr(2, 9);
    this.kind = kind;
    this.label = `Mock ${kind} track`;
    this.enabled = true;
    this.muted = false;
    this.readyState = 'live';
    
    this.onended = null;
    this.onmute = null;
    this.onunmute = null;
  }

  stop() {
    this.readyState = 'ended';
    if (this.onended) {
      this.onended();
    }
  }

  clone() {
    const cloned = new MediaStreamTrack(this.kind);
    cloned.enabled = this.enabled;
    return cloned;
  }
};

// Mock WebSocket
global.WebSocket = class WebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  constructor(url, protocols) {
    this.url = url;
    this.protocols = protocols;
    this.readyState = WebSocket.CONNECTING;
    this.bufferedAmount = 0;
    
    this.onopen = null;
    this.onclose = null;
    this.onerror = null;
    this.onmessage = null;
    
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }, 10);
  }

  send(data) {
    if (this.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    // Simulate successful send
  }

  close(code, reason) {
    this.readyState = WebSocket.CLOSING;
    setTimeout(() => {
      this.readyState = WebSocket.CLOSED;
      if (this.onclose) {
        this.onclose({ code, reason });
      }
    }, 10);
  }

  // Helper methods for testing
  _simulateMessage(data) {
    if (this.onmessage) {
      this.onmessage({ data });
    }
  }

  _simulateError(error) {
    if (this.onerror) {
      this.onerror(error);
    }
  }

  _simulateClose(code = 1000, reason = '') {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose({ code, reason });
    }
  }
};

// Mock DOM elements - Use jsdom's document but override getElementById
// Store the original method
const originalGetElementById = document.getElementById.bind(document);

// Create mock element cache
const mockElementCache = new Map();

// Helper to create mock video element
function createMockVideoElement(id) {
  if (!mockElementCache.has(id)) {
    const elem = {
      id,
      tagName: 'VIDEO',
      textContent: '',
      classList: {
        add: jest.fn(),
        remove: jest.fn(),
        contains: jest.fn(() => false),
        _classes: new Set()
      },
      _srcObject: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      play: jest.fn().mockResolvedValue(undefined),
      pause: jest.fn(),
    };
    
    // Add srcObject getter/setter
    Object.defineProperty(elem, 'srcObject', {
      get() { return this._srcObject; },
      set(value) { 
        this._srcObject = value;
      },
      configurable: true,
      enumerable: true
    });
    
    mockElementCache.set(id, elem);
  }
  return mockElementCache.get(id);
}

// Override document.getElementById to return mocks for our specific elements
document.getElementById = jest.fn((id) => {
  if (id === 'remoteVideo' || id === 'videoOverlay') {
    return createMockVideoElement(id);
  }
  if (id === 'iceState' || id === 'signalingState' || id === 'dataChannelState') {
    // Return a simple mock element for status displays
    if (!mockElementCache.has(id)) {
      mockElementCache.set(id, {
        id,
        textContent: '',
        classList: {
          add: jest.fn(),
          remove: jest.fn()
        }
      });
    }
    return mockElementCache.get(id);
  }
  // Fall back to original for other elements
  return originalGetElementById(id);
});

// Export helper for tests to simulate network conditions
global.simulateNetworkConditions = {
  // Simulate packet loss
  packetLoss: (percentage) => {
    return Math.random() * 100 > percentage;
  },
  
  // Simulate latency
  addLatency: (callback, ms) => {
    return new Promise(resolve => {
      setTimeout(() => {
        callback();
        resolve();
      }, ms);
    });
  },
  
  // Simulate bandwidth limitation
  simulateBandwidthLimit: (dataSize, bandwidthKbps) => {
    const transmissionTimeMs = (dataSize * 8) / (bandwidthKbps * 1000) * 1000;
    return transmissionTimeMs;
  }
};
