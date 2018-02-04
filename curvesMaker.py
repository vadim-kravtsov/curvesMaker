#! /usr/bin/env python

import sys
from GUI import MainApplication

if __name__ == "__main__":
    if len(sys.argv) > 1:
        imageName = sys.argv[1]
    else:
        imageName = None
    MainApplication(imageName)

