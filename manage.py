#!/usr/bin/env python
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    # manager.run()
    app.run(host="0.0.0.0", debug=True)