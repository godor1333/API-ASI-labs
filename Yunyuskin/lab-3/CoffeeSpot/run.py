#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrapper script to run the LabyrinthAI project"""
import os
import sys

# Change to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Now import and run main
if __name__ == "__main__":
    exec(open('main.py').read())
