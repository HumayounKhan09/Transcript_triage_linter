#!/usr/bin/env python3
"""
Root-level CLI wrapper.
"""
import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engines.cli import CLI


if __name__ == "__main__":
    CLI().main()
