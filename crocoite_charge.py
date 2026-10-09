#!/usr/bin/env python3
"""Crocoite Charge — neon charge-sweep arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/CROCOITE_CHARGE_ElbowOS.mp4")
TITLE, HANDLE = "CROCOITE CHARGE", "x.com/ElbowOS"
BG, COPPER, TEAL = (16, 7, 8), (255, 124, 40), (52, 236, 198)
GOLD, MAG = (255, 214, 92), (255, 62, 138)
COLS, ROWS, CELL = 5, 8, 168
OX, OY = (W - COLS * CELL) // 2, 360
NUM_C = {1: (64, 220, 210), 2: (130, 230, 88), 3: (255, 196, 70), 4: (255, 118, 54),
         5: (255, 70, 140), 6: (186, 126, 255), 7: (255, 255, 255), 8: (200, 206, 214)}

class Game:
    def __init__(self):
        pygame.init(); pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit(); pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 52, bold=True)
        self.big = pygame.font.SysFont("dejavusans", 84, bold=True)
        self.numf = pygame.font.SysFont("dejavusans", 70, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.score = 0
        self.sparks, self.embers = [], []
        self.reset(keep=False)

    def reset(self, keep=True):
        score = self.score if keep else 0
        self.mines = [[False] * COLS for _ in range(ROWS)]
        self.open = [[False] * COLS for _ in range(ROWS)]
        self.flag = [[False] * COLS for _ in range(ROWS)]
        self.anim = [[0.0] * COLS for _ in range(ROWS)]
        spots = [(c, r) for c in range(COLS) for r in range(ROWS)]
        random.shuffle(spots)
        for c, r in spots[:8]:
            self.mines[r][c] = True
        self.cx, self.cy = 2, 3
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                rr, cc = self.cy + dr, self.cx + dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    self.mines[rr][cc] = False
        self.score, self.combo, self.flash = score, 0, 0
        self.px = self.tx = OX + self.cx * CELL + CELL / 2
        self.py = self.ty = OY + self.cy * CELL + CELL / 2
        if not self.embers:
            self.embers = [[random.randrange(W), random.randrange(H), random.uniform(0.5, 1.8)] for _ in range(48)]
        self.tick = getattr(self, "tick", 0)
        self.dwell = 0
        self.reveal(self.cx, self.cy)
        self.plan = self._plan()
        self.pi = 0
        if self.plan:
            _, c, r = self.plan[0]
            self.tx = OX + c * CELL + CELL / 2
            self.ty = OY + r * CELL + CELL / 2

    def count(self, c, r):
        return sum(self.mines[r + dr][c + dc]
                   for dc in (-1, 0, 1) for dr in (-1, 0, 1)
                   if (dc or dr) and 0 <= c + dc < COLS and 0 <= r + dr < ROWS)

    def burst(self, c, r, col):
        x, y = OX + c * CELL + CELL / 2, OY + r * CELL + CELL / 2
        for i in range(10):
            a = i * math.tau / 10 + random.random() * 0.3
            sp = 4 + random.random() * 5
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, col, 16])

    def reveal(self, c, r):
        if not (0 <= c < COLS and 0 <= r < ROWS) or self.open[r][c] or self.flag[r][c]:
            return
        if self.mines[r][c]:
            self.flag[r][c] = True
            self.score += 40
            self.flash = 8
            self.burst(c, r, MAG)
            return
        stack = [(c, r)]
        while stack:
            cc, rr = stack.pop()
            if self.open[rr][cc] or self.mines[rr][cc]:
                continue
            self.open[rr][cc] = True
            self.anim[rr][cc] = 1.0
            self.score += 10 + self.combo
            self.combo = min(14, self.combo + 1)
            self.burst(cc, rr, TEAL if self.count(cc, rr) == 0 else GOLD)
            if self.count(cc, rr) == 0:
                for dc in (-1, 0, 1):
                    for dr in (-1, 0, 1):
                        nc, nr = cc + dc, rr + dr
                        if 0 <= nc < COLS and 0 <= nr < ROWS and not self.open[nr][nc]:
                            stack.append((nc, nr))

    def _plan(self):
        cells = []
        for r in range(ROWS):
            cols = range(COLS) if r % 2 == 0 else range(COLS - 1, -1, -1)
            for c in cols:
                if not self.mines[r][c] and not self.open[r][c]:
                    cells.append(("open", c, r))
        for r in range(ROWS):
            for c in range(COLS):
                if self.mines[r][c]:
                    cells.append(("flag", c, r))
        return cells

    def step(self, auto=False):
        self.tick += 1
        self.flash = max(0, self.flash - 1)
        for e in self.embers:
            e[1] -= e[2]
            if e[1] < 0:
                e[0], e[1] = random.randrange(W), H + 4
        for s in self.sparks:
            s[0] += s[2]; s[1] += s[3]; s[5] -= 1
        self.sparks = [s for s in self.sparks if s[5] > 0]
        for r in range(ROWS):
            for c in range(COLS):
                if self.anim[r][c] > 0:
                    self.anim[r][c] = max(0.0, self.anim[r][c] - 0.1)
        self.px += (self.tx - self.px) * 0.34
        self.py += (self.ty - self.py) * 0.34
        if not auto:
            return
        self.dwell += 1
        arrived = abs(self.px - self.tx) < 10 and abs(self.py - self.ty) < 10
        if self.pi < len(self.plan) and arrived and self.dwell > 3:
            kind, c, r = self.plan[self.pi]
            if kind == "open":
                self.reveal(c, r)
            elif not self.flag[r][c]:
                self.flag[r][c] = True
                self.score += 55
                self.burst(c, r, MAG)
                self.flash = 6
            self.pi += 1
            self.dwell = 0
            if self.pi < len(self.plan):
                _, c, r = self.plan[self.pi]
                self.tx = OX + c * CELL + CELL / 2
                self.ty = OY + r * CELL + CELL / 2
            else:
                self.reset(keep=True)
        elif self.pi >= len(self.plan):
            self.reset(keep=True)

    def draw(self, surf):
        surf.fill(BG)
        for i in range(9):
            y = (self.tick * 3 + i * 230) % (H + 180) - 90
            pygame.draw.line(surf, (62, 22, 16), (0, y), (W, y - 70), 2)
        for e in self.embers:
            pygame.draw.circle(surf, (190, 78, 32), (int(e[0]), int(e[1])), 3)
        title = self.big.render(TITLE, True, COPPER)
        surf.blit(title, title.get_rect(center=(W // 2, 118)))
        sub = self.small.render("NEON CHARGE SWEEP", True, TEAL)
        surf.blit(sub, sub.get_rect(center=(W // 2, 186)))
        sc = self.font.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 258)))
        plate = pygame.Rect(OX - 20, OY - 20, COLS * CELL + 40, ROWS * CELL + 40)
        pygame.draw.rect(surf, (34, 14, 16), plate, border_radius=20)
        pygame.draw.rect(surf, COPPER, plate, 4, border_radius=20)
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(OX + c * CELL + 8, OY + r * CELL + 8, CELL - 16, CELL - 16)
                if self.open[r][c]:
                    pygame.draw.rect(surf, (46, 20, 24), rect, border_radius=14)
                    n = self.count(c, r)
                    if n:
                        t = self.numf.render(str(n), True, NUM_C.get(n, TEAL))
                        surf.blit(t, t.get_rect(center=rect.center))
                    else:
                        pygame.draw.circle(surf, (92, 42, 36), rect.center, 12)
                else:
                    shade = (78, 32, 22) if (c + r) % 2 == 0 else (60, 24, 18)
                    pygame.draw.rect(surf, shade, rect, border_radius=14)
                    pygame.draw.rect(surf, (156, 70, 38), rect, 3, border_radius=14)
                    if self.flag[r][c]:
                        pygame.draw.line(surf, TEAL, (rect.centerx, rect.bottom - 16), (rect.centerx, rect.top + 20), 5)
                        pygame.draw.polygon(surf, MAG, [(rect.centerx, rect.top + 16), (rect.centerx + 38, rect.top + 36), (rect.centerx, rect.top + 50)])
                if self.anim[r][c] > 0:
                    a = self.anim[r][c]
                    pygame.draw.rect(surf, GOLD, rect.inflate(-int(50 * (1 - a)), -int(50 * (1 - a))), 4, border_radius=12)
        pygame.draw.line(surf, (255, 170, 80), (int(self.px), int(self.py)), (int(self.tx), int(self.ty)), 3)
        pulse = 8 + 5 * math.sin(self.tick / 3)
        pygame.draw.circle(surf, (255, 186, 96), (int(self.px), int(self.py)), int(30 + pulse), 4)
        pygame.draw.circle(surf, COPPER, (int(self.px), int(self.py)), 13)
        pygame.draw.circle(surf, GOLD, (int(self.px), int(self.py)), 5)
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1])), max(2, s[5] // 4))
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 90, 40, 46))
            surf.blit(veil, (0, 0))
        hb = self.font.render(HANDLE, True, TEAL)
        surf.blit(hb, hb.get_rect(center=(W // 2, H - 108)))
        hint = self.small.render("ARROWS MOVE   SPACE REVEAL   F FLAG", True, (214, 154, 122))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 48)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_LEFT, pygame.K_a):
                        self.cx = max(0, self.cx - 1)
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        self.cx = min(COLS - 1, self.cx + 1)
                    elif ev.key in (pygame.K_UP, pygame.K_w):
                        self.cy = max(0, self.cy - 1)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        self.cy = min(ROWS - 1, self.cy + 1)
                    elif ev.key == pygame.K_SPACE:
                        self.reveal(self.cx, self.cy)
                    elif ev.key == pygame.K_f and not self.open[self.cy][self.cx]:
                        self.flag[self.cy][self.cx] = not self.flag[self.cy][self.cx]
                    elif ev.key == pygame.K_r:
                        self.reset(keep=False)
                    self.tx = OX + self.cx * CELL + CELL / 2
                    self.ty = OY + self.cy * CELL + CELL / 2
            self.step(False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(True)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0 or not os.path.exists(OUT) or os.path.getsize(OUT) < 2000:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, os.path.getsize(OUT))
        pygame.quit()

def main():
    g = Game()
    g.play_interactive() if PLAY and not RECORD else g.record()

if __name__ == "__main__":
    main()
