import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH for tests invoked from subdirs
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
