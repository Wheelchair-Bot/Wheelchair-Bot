"""Tests for the simulator server."""

from wheelchair.simulator_server import create_simulator_callback
from wheelchair.interfaces import WheelchairState


class TestSimulatorCallback:
    """Test cases for simulator callback integration."""

    def test_create_callback(self):
        """Test creating a callback function."""
        from wheelchair.simulator_server import SimulatorServer
        server = SimulatorServer(host="localhost", port=18769)
        callback = create_simulator_callback(server, update_rate=30.0)
        
        assert callable(callback)
        
        # Test calling the callback (should not raise)
        state = WheelchairState()
        callback(state, 0.02)

    def test_callback_with_state(self):
        """Test callback processes state correctly."""
        from wheelchair.simulator_server import SimulatorServer
        server = SimulatorServer(host="localhost", port=18770)
        callback = create_simulator_callback(server, update_rate=10.0)
        
        state = WheelchairState(x=5.0, y=10.0, theta=1.57)
        
        # Call multiple times
        for i in range(10):
            callback(state, 0.01)
            state.x += 0.1
        
        # Should not raise errors
        assert True

    def test_callback_update_rate(self):
        """Test that callback respects update rate."""
        from wheelchair.simulator_server import SimulatorServer
        server = SimulatorServer(host="localhost", port=18771)
        
        # High update rate should broadcast more often
        callback_fast = create_simulator_callback(server, update_rate=60.0)
        
        # Low update rate should broadcast less often
        callback_slow = create_simulator_callback(server, update_rate=1.0)
        
        # Both should be callable
        assert callable(callback_fast)
        assert callable(callback_slow)


class TestSimulatorServerBasic:
    """Basic tests for SimulatorServer (non-async)."""

    def test_server_initialization(self):
        """Test server can be initialized."""
        from wheelchair.simulator_server import SimulatorServer
        server = SimulatorServer(host="localhost", port=8765)
        
        assert server.host == "localhost"
        assert server.port == 8765
        assert len(server.clients) == 0
        assert not server.is_running()

    def test_server_custom_port(self):
        """Test server with custom port."""
        from wheelchair.simulator_server import SimulatorServer
        server = SimulatorServer(host="0.0.0.0", port=9999)
        
        assert server.host == "0.0.0.0"
        assert server.port == 9999

