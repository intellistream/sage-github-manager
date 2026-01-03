"""Test package"""

from pathlib import Path
import sys

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
