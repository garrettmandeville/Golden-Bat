"""
Golden Bat - Main Entry Point

Author: Garrett Mandeville
Description: Launches the game. The engine lives in the goldenbat package and all
             story content lives in the data folder.
"""

import sys
from goldenbat.game import run

if __name__ == "__main__":
    # Story text uses characters like "Ō"; never crash on a terminal that can't show them
    sys.stdout.reconfigure(errors = "replace")
    run()
