# Crocoite Charge

Full-colour Python 3 neon charge-sweep arcade for ElbowOS.

A copper probe glides over a 5×8 vein board. Open a safe cell and empty pockets chain-clear. Hot veins take a magenta flag instead of a blast. Arrows move. Space reveals. F flags. R restarts.

Not a Nintendo ROM or emulator. Original board, original art.

## Play

```
pip install -r requirements.txt
python3 crocoite_charge.py --play
```

## Record a 9:16 reel

```
python3 crocoite_charge.py --record
```

Writes a 1080x1920 h264 clip (15s @ 30fps) with title, score, and `x.com/ElbowOS` burned into the frames. Headless runs use `SDL_VIDEODRIVER=dummy`.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1qG1FWJi_9eeiS1UhqdXVwXg-MSOQ3yR2/view
- Posted copy: https://drive.google.com/file/d/1P6lcmo0iar_hRZFg3zUH7D1sQpOJQDPG/view
