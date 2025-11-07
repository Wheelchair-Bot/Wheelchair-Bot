#!/usr/bin/env python3
"""
Example script demonstrating how to control the wheelchair programmatically
This shows how to use the WebSocket API to send commands
"""
import asyncio
import websockets
import json
import time
from datetime import datetime


async def control_example():
    """
    Example control sequence demonstrating basic movements
    """
    uri = "ws://localhost:8000/ws/commands"
    
    print("Connecting to teleopd service...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✓ Connected: {data}")
            
            if data.get("estop_active"):
                print("⚠ E-stop is active. Please reset before controlling.")
                return
            
            # Define a sequence of movements
            movements = [
                {"type": "move", "direction": "forward", "speed": 0.3, "duration": 2},
                {"type": "stop", "duration": 1},
                {"type": "move", "direction": "left", "speed": 0.5, "duration": 1},
                {"type": "stop", "duration": 1},
                {"type": "move", "direction": "right", "speed": 0.5, "duration": 1},
                {"type": "stop", "duration": 1},
                {"type": "move", "direction": "backward", "speed": 0.3, "duration": 2},
                {"type": "stop", "duration": 0},
            ]
            
            print("\n" + "="*60)
            print("Starting movement sequence...")
            print("Press Ctrl+C to trigger emergency stop")
            print("="*60 + "\n")
            
            for i, movement in enumerate(movements, 1):
                duration = movement.pop("duration")
                movement["timestamp"] = time.time()
                
                # Send command
                print(f"[{i}/{len(movements)}] Sending: {movement['type']}", end="")
                if movement.get("direction"):
                    print(f" {movement['direction']} @ {movement['speed']*100:.0f}%", end="")
                print()
                
                await websocket.send(json.dumps(movement))
                
                # Wait for acknowledgment
                response = await websocket.recv()
                ack = json.loads(response)
                
                if ack.get("type") == "error":
                    print(f"✗ Error: {ack['message']}")
                    break
                elif ack.get("type") == "ack":
                    print(f"  ✓ Acknowledged")
                
                # Execute movement for duration
                if duration > 0:
                    print(f"  ⏱ Executing for {duration}s...")
                    await asyncio.sleep(duration)
            
            print("\n" + "="*60)
            print("✓ Movement sequence completed")
            print("="*60)
            
    except websockets.exceptions.ConnectionClosed:
        print("✗ Connection closed")
    except KeyboardInterrupt:
        print("\n\n⚠ Emergency stop triggered by user!")
        # Send e-stop command
        async with websockets.connect(uri) as ws:
            estop_cmd = {"type": "estop", "timestamp": time.time()}
            await ws.send(json.dumps(estop_cmd))
            print("✓ E-stop command sent")
    except Exception as e:
        print(f"✗ Error: {e}")


async def get_status():
    """
    Get current status from all services
    """
    import aiohttp
    
    services = {
        "Teleopd": "http://localhost:8000/status",
        "Streamer": "http://localhost:8001/status",
        "Safety Agent": "http://localhost:8002/status",
        "Net Agent": "http://localhost:8003/status",
    }
    
    print("\n" + "="*60)
    print("Service Status")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        for name, url in services.items():
            try:
                async with session.get(url, timeout=2) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"\n{name}:")
                        print(f"  {json.dumps(data, indent=2)}")
                    else:
                        print(f"\n{name}: ✗ Status {resp.status}")
            except Exception as e:
                print(f"\n{name}: ✗ {str(e)}")
    
    print("\n" + "="*60)


async def simple_control():
    """
    Simple manual control via command line
    """
    uri = "ws://localhost:8000/ws/commands"
    
    print("Simple Wheelchair Control")
    print("Commands: w=forward, s=backward, a=left, d=right, x=stop, q=quit, e=estop")
    print("Speed: 1-9 (default: 5)")
    print()
    
    speed = 0.5
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        response = await websocket.recv()
        print(f"Connected: {json.loads(response)}\n")
        
        print("Ready for commands. Type and press Enter:")
        
        while True:
            try:
                cmd = input("> ").lower().strip()
                
                if not cmd:
                    continue
                
                if cmd == 'q':
                    break
                elif cmd == 'e':
                    command = {"type": "estop", "timestamp": time.time()}
                elif cmd == 'x':
                    command = {"type": "stop", "timestamp": time.time()}
                elif cmd in ['w', 'a', 's', 'd']:
                    direction_map = {
                        'w': 'forward',
                        's': 'backward',
                        'a': 'left',
                        'd': 'right'
                    }
                    command = {
                        "type": "move",
                        "direction": direction_map[cmd],
                        "speed": speed,
                        "timestamp": time.time()
                    }
                elif cmd.isdigit() and 1 <= int(cmd) <= 9:
                    speed = int(cmd) / 10
                    print(f"Speed set to {speed*100:.0f}%")
                    continue
                else:
                    print("Unknown command")
                    continue
                
                # Send command
                await websocket.send(json.dumps(command))
                
                # Get response
                response = await websocket.recv()
                ack = json.loads(response)
                
                if ack.get("type") == "error":
                    print(f"Error: {ack['message']}")
                elif ack.get("type") == "ack":
                    print(f"✓ {command['type']}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Usage: python example_control.py [mode]")
        print("Modes:")
        print("  demo    - Run automated movement sequence")
        print("  status  - Show status of all services")
        print("  control - Simple keyboard control")
        print()
        print("Example: python example_control.py demo")
        return
    
    if mode == "demo":
        print("Running automated demo sequence...\n")
        asyncio.run(control_example())
    elif mode == "status":
        print("Fetching service status...\n")
        asyncio.run(get_status())
    elif mode == "control":
        print("Starting keyboard control...\n")
        asyncio.run(simple_control())
    else:
        print(f"Unknown mode: {mode}")
        print("Valid modes: demo, status, control")


if __name__ == "__main__":
    main()
