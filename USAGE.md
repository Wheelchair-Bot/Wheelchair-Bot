# Example Usage

## Opening the Controller

Simply open `index.html` in your web browser. No build step or dependencies required!

### Recommended Browsers
- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Safari

## Testing Without a Server

You can test the UI and controls without a backend server:

1. Open `index.html` in your browser
2. Interact with the control buttons - they will respond visually
3. Check the browser console to see logged control commands
4. The interface will show "WebRTC not ready" warnings until connected to a server

## Connecting to a Backend

To fully test the WebRTC functionality, you'll need a signaling server. Here's a minimal example structure:

### Expected Server Behavior

The signaling server should:

1. Accept WebSocket connections on the configured port (e.g., `ws://localhost:8080`)
2. Handle these message types:
   - `offer`: Respond with an `answer` containing SDP
   - `ice-candidate`: Forward ICE candidates
   - `answer`: Process the WebRTC answer

3. Send video stream to the client via WebRTC
4. Listen for control commands on the data channel

### Command Format Received by Server

```json
{
  "type": "movement",
  "direction": "forward",  // or "backward", "left", "right", "stop"
  "speed": 50,             // 0-100
  "timestamp": 1699999999999
}
```

## Control Methods

### 1. On-Screen Buttons
Click and hold the directional buttons to move. Release to stop.

### 2. Keyboard Controls
- **W** or **↑**: Forward
- **S** or **↓**: Backward  
- **A** or **←**: Left
- **D** or **→**: Right
- **Space** or **Esc**: Stop

### 3. Touch Controls (Mobile)
Tap and hold the directional buttons on touch devices.

## Speed Control

Use the slider to adjust movement speed from 0% to 100%. The speed value is sent with each movement command.

## Monitoring Connection

The interface shows three connection states:

1. **Connection Status** (top right): Overall connection state
   - 🔴 Disconnected
   - 🟠 Connecting...
   - 🟢 Connected

2. **ICE Connection**: WebRTC ICE connection state
3. **Signaling**: WebRTC signaling state  
4. **Data Channel**: Control command channel state

## Troubleshooting

### "Connection Failed"
- Verify the server URL is correct
- Ensure the signaling server is running
- Check for firewall issues

### "WebRTC not ready"
- Wait for the connection to be fully established
- Check that all three states (ICE, Signaling, Data Channel) are "connected"/"open"

### No Video Stream
- Ensure the server is sending video tracks
- Check browser console for errors
- Verify camera permissions if testing locally

## Development Tips

### Serving Locally

Use any static file server:

```bash
# Python
python -m http.server 8000

# Node.js  
npx http-server

# PHP
php -S localhost:8000
```

Then open: `http://localhost:8000`

### Browser Console

Open browser developer tools (F12) to:
- See connection logs
- Monitor command transmission
- Debug WebRTC issues
- View ICE candidate exchange
