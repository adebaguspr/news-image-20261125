#!/usr/bin/env python3
"""Entry point (Python 3.13, standard library only): copy the image beside
this file to /output/entry.png. Deterministic: byte-identical every run.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
shutil.copyfile(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"),
    os.path.join(out_dir, "entry.png"),
)
