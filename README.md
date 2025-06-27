# ARTSEY

This repository defines the one‑handed ARTSEY keyboard layout.

## Simulator

A small Python script `artsey/simulate.py` can be used to try the layout on a regular keyboard.
Install dependencies and run it with eight keys that represent the ARTSEY grid.
For example, to use the right hand keys `p o i u ç l k j`:

```bash
pip install pyyaml pynput
python artsey/simulate.py --hand right p o i u ç l k j
```

Press the selected keys in combinations to see the mapped characters in the terminal.
Press `Esc` to exit.

