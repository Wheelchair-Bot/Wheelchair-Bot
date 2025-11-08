# WebRTC Video Send/Receive Tests

This directory contains comprehensive tests for the WebRTC video streaming functionality in the Wheelchair Bot application.

## Test Coverage

The tests verify all aspects of WebRTC communication:

### 1. Connection Lifecycle
- **Connection Establishment**: Tests WebSocket connection, peer connection initialization, and data channel creation
- **Connection Teardown**: Ensures proper cleanup of all WebRTC resources
- **Reconnection Handling**: Validates ability to reconnect after disconnection

### 2. Video Stream Send/Receive
- **Video Receive**: Tests receiving video streams, hiding overlays, handling multiple tracks, and stream quality
- **Video Send**: Tests adding local video tracks and handling multiple streams
- **Stream Continuity**: Verifies video streams remain active over time

### 3. Error Handling
- **Transmission Failures**: Tests handling of WebSocket errors, data channel failures, and peer connection errors
- **Connection Interruptions**: Tests ICE connection failures, unexpected disconnections, and track ending
- **Signaling Errors**: Tests handling of invalid signaling messages and missing data

### 4. Performance Under Network Conditions
- **Network Latency**: Tests high latency connections and variable latency in data channels
- **Bandwidth Limitations**: Tests transmission time estimation and data channel buffering
- **Packet Loss**: Simulates intermittent packet loss scenarios
- **Connection Recovery**: Tests temporary connection loss and ICE connection restart

### 5. Platform Compatibility
- **WebRTC API Availability**: Verifies all required WebRTC APIs are available
- **Browser Feature Support**: Tests RTCPeerConnection, offers/answers, data channels, and track handling
- **Cross-Platform Video Codecs**: Tests different video track configurations and audio+video combinations
- **Data Channel Compatibility**: Tests ordered/unordered data channels and state transitions

### 6. Integration Tests
- Tests the complete WebRTC workflow including connection, video streaming, command sending, and disconnection

## Running the Tests

### Run All Tests
```bash
npm test
```

### Run Specific WebRTC Tests
```bash
npm run test:webrtc
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

## Test Files

- `webrtc.test.js` - Main test suite with all WebRTC functionality tests
- `setup.js` - Test setup file that mocks WebRTC APIs and DOM elements
- `jest.config.js` - Jest configuration for the test environment

## Test Architecture

The tests use:
- **Jest** as the test framework
- **jsdom** for browser environment simulation
- **Mock WebRTC APIs** including RTCPeerConnection, MediaStream, MediaStreamTrack, and WebSocket
- **Mock DOM elements** for video players and UI components

## Mock Implementation

The test setup provides comprehensive mocks for:
- `RTCPeerConnection` with full signaling support
- `MediaStream` and `MediaStreamTrack` for video/audio handling
- `WebSocket` for signaling channel
- DOM elements (`remoteVideo`, `videoOverlay`, etc.)
- Network simulation helpers for latency, bandwidth, and packet loss

## Writing New Tests

When adding new WebRTC features, add corresponding tests in `webrtc.test.js`:

1. Add a new `describe` block for your feature area
2. Use `beforeEach` to set up a fresh WebRTCManager instance
3. Use helper methods like `_simulateTrack`, `_simulateConnectionState`, etc. to simulate WebRTC events
4. Clean up in `afterEach` to prevent test pollution

Example:
```javascript
describe('My New Feature', () => {
  test('should do something', async () => {
    await manager.connect('ws://localhost:8080');
    await new Promise(resolve => setTimeout(resolve, 50));
    
    // Your test assertions here
    expect(manager.isConnected).toBe(true);
  });
});
```

## Test Results

All 60 tests pass successfully, covering:
- 16 connection lifecycle tests
- 8 video send/receive tests
- 13 error handling tests  
- 7 performance tests
- 13 platform compatibility tests
- 3 integration tests

## Continuous Integration

These tests should be run as part of the CI/CD pipeline to ensure WebRTC functionality remains stable across code changes.
