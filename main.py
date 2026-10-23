"""Root entry point for Spectrum Shift."""

import sys
import asyncio
from pathlib import Path

# Ensure workspace root is in python path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spectrum_shift.main import main

if __name__ == "__main__":
    asyncio.run(main())
