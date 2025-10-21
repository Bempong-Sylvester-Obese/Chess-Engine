import os
import sys
from app import app

sys.path.insert(0, os.path.dirname(__file__))

application = app

if __name__ == "__main__":
    app.run()
