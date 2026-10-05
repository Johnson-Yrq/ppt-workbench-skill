#!/usr/bin/env python3
"""Build the approved marble specimen with the shared production builder."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PACK = REPO / 'skills/monochrome-marble-slides'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['speech', 'reading'], default='speech')
    args = parser.parse_args()
    source = 'deck.example.json' if args.mode == 'speech' else 'deck.reading.example.json'
    filename = '黑白大理石商务-中文风格样稿.html' if args.mode == 'speech' else '黑白大理石商务-阅读型样稿.html'
    subprocess.run([sys.executable, str(REPO / 'skills/white-blue-slides/scripts/build_deck.py'),
                    str(PACK / 'assets' / source), '--embed-format', 'keep', '--out', str(ROOT / filename)], check=True)


if __name__ == '__main__':
    main()
