#! /usr/bin/env python

import sys
from os import path, getcwd
sys.path.append(path.join(getcwd(), "lib"))
from lib.GUI import MainApplication
from lib.settings import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        imageName = sys.argv[1]
    else:
        imageName = None
    MainApplication(imageName)

