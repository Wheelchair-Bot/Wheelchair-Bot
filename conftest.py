"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
root_path = Path(__file__).parent.resolve()
src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
