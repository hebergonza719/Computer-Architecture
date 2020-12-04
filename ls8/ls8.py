#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

print("here", sys.argv[1])

cpu = CPU()

cpu.load()
cpu.run()