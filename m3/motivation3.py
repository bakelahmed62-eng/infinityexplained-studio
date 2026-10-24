import subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, S = 1080, 1920, 24, 2
BG = (9, 14, 28)
WHITE = (255, 255, 255)
BLUE = (45, 156, 255)
AMBER = (245, 165, 36)
MUTED = (170, 180, 195)
IVORY = (238, 240, 246)
SILVER = (190, 200, 215)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
CX, CY = 540, 1090

HOOK = 'You are not behind. You are becoming someone new.'
LINES = ['Psychologists call it your possible self, the person you picture growing into.',
         'Research suggests that picturing your future self clearly can guide what you do today.',
         'So take one small step toward them now.']
CTA = 'Follow INFINITYEXPLAINED for a new idea every day.'
QUESTION = 'What would your future self thank you for today?'
KEYS = ['becoming', 'possible', 'self', 'future', 'step', 'today', 'small', 'new']

FONTS = {}


def font(path, size):
    k = (path, size)
    if k not in FONTS:
        FONTS[k] = ImageFont.truetype(path, int(size * S))
    return FONTS[k]


def narration():
    return ' '.join([HOOK] + LINES + [CTA, QUESTION])


def duration(wav):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav])
    return float(out.decode().strip())


def clamp(x):
    return max(0.0, min(1.0, x))


def eo(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def scene(t, start, end, fade=0.45):
    return eio((t - start) / fade) * eio((end - t) / fade)


def mix(c, a):
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))


class Pen:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def rect(self, b, fill, r=0):
        bb = [v * S for v in b]
        if r:
            self.d.rounded_rectangle(bb, radius=r * S, fill=fill)
        else:
            self.d.rectangle(bb, fill=fill)

    def ell(self, b, fill=None, outline=None, width=1):
        self.d.ellipse([v * S for v in b], fill=fill, outline=outline, width=max(1, int(width * S)))

    def line(self, p, q, fill, width):
        self.d.line([p[0] * S, p[1] * S, q[0] * S, q[1] * S], fill=fill, width=max(1, int(width * S)))

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def text(self, xy, s, f, fill, anchor='ma'):
        self.d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill, anchor=anchor)

    def width(self, s, f):
        return self.d.textlength(s, font=f) / S


def make_bg():
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    seed = 12345
    palette = [(14, 26, 62), (22, 48, 104), (10, 18, 44), (30, 78, 150), (40, 110, 190), (70, 60, 40)]
    for n in range(9000):
        seed = (seed * 1103515245 + 12345) % 2147483648
        x = seed % W
        seed = (seed * 1103515245 + 12345) % 2147483648
        y = seed % H
        seed = (seed * 1103515245 + 12345) % 2147483648
        jit = (seed % 100) / 100.0
        dx, dy = x - CX, (y - CY) * 0.8
        r = math.hypot(dx, dy)
        ang = math.atan2(dy, dx) + math.pi / 2 + 0.7 * math.exp(-r / 600.0) + (jit - 0.5) * 0.5
        near = clamp(1.0 - r / 760.0)
        if near > 0.55 and jit > 0.45:
            c = (int(120 + 125 * near), int(80 + 85 * near), int(20 + 16 * near))
        else:
            c = palette[int(jit * 5.99)]
        ln = 20 + jit * 22
        x2, y2 = x + math.cos(ang) * ln, y + math.sin(ang) * ln
        d.line([x, y, x2, y2], fill=c, width=int(7 + jit * 6))
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    img = Image.blend(Image.new('RGB', (W, H), BG), img, 0.72)
    shade = Image.new('L', (1, H))
    px = shade.load()
    for y in range(H):
        k = y / float(H)
        px[0, y] = int(255 * (0.30 + 0.70 * eio((k - 0.12) / 0.5)))
    shade = shade.resize((W, H))
    dark = Image.new('RGB', (W, H), BG)
    img = Image.composite(img, dark, shade)
    return img.resize((W * S, H * S), Image.LANCZOS)


BGIMG = None


def wrap(pen, text, f, maxw):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if pen.width(test, f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def rich(pen, y, text, f, base, a, maxw, lead, slide=1.0):
    if a <= 0.02:
        return
    y = y + (1.0 - slide) * 34
    for line in wrap(pen, text, f, maxw):
        words = line.split(' ')
        total = pen.width(line, f)
        x = W / 2 - total / 2
        for wd in words:
            clean = wd.lower().strip('.,?!')
            col = AMBER if clean in KEYS else base
            pen.text((x, y), wd, f, mix(col, a), anchor='la')
            x += pen.width(wd + ' ', f)
        y += lead


def pill(pen, cx, y, label, a):
    if a <= 0.02:
        return
    f = font(FB, 38)
    tw = pen.width(label, f)
    pen.rect([cx - tw / 2 - 36, y, cx + tw / 2 + 36, y + 84], mix((15, 42, 69), a), r=42)
    pen.text((cx, y + 14), label, f, mix(BLUE, a))


def pawn(pen, cx, by, h, a, col=IVORY):
    c = mix(col, a)
    sh = mix((150, 158, 175), a)
    pen.ell([cx - 0.30 * h, by - 0.07 * h, cx + 0.30 * h, by + 0.03 * h], fill=sh)
    pen.poly([(cx - 0.20 * h, by - 0.03 * h), (cx + 0.20 * h, by - 0.03 * h), (cx + 0.08 * h, by - 0.56 * h), (cx - 0.08 * h, by - 0.56 * h)], c)
    pen.poly([(cx + 0.02 * h, by - 0.03 * h), (cx + 0.20 * h, by - 0.03 * h), (cx + 0.08 * h, by - 0.56 * h), (cx + 0.02 * h, by - 0.56 * h)], sh)
    pen.ell([cx - 0.16 * h, by - 0.62 * h, cx + 0.16 * h, by - 0.54 * h], fill=c)
    pen.ell([cx - 0.12 * h, by - 0.82 * h, cx + 0.12 * h, by - 0.58 * h], fill=c)


def king(pen, cx, by, h, a, col=IVORY):
    c = mix(col, a)
    sh = mix((150, 158, 175), a)
    pen.ell([cx - 0.32 * h, by - 0.06 * h, cx + 0.32 * h, by + 0.03 * h], fill=sh)
    pen.poly([(cx - 0.22 * h, by - 0.03 * h), (cx + 0.22 * h, by - 0.03 * h), (cx + 0.09 * h, by - 0.66 * h), (cx - 0.09 * h, by - 0.66 * h)], c)
    pen.poly([(cx + 0.02 * h, by - 0.03 * h), (cx + 0.22 * h, by - 0.03 * h), (cx + 0.09 * h, by - 0.66 * h), (cx + 0.02 * h, by - 0.66 * h)], sh)
    pen.ell([cx - 0.17 * h, by - 0.71 * h, cx + 0.17 * h, by - 0.63 * h], fill=c)
    pen.poly([(cx - 0.13 * h, by - 0.70 * h), (cx + 0.13 * h, by - 0.70 * h), (cx + 0.17 * h, by - 0.86 * h), (cx - 0.17 * h, by - 0.86 * h)], c)
    pen.rect([cx - 0.19 * h, by - 0.89 * h, cx + 0.19 * h, by - 0.85 * h], c, r=2)
    pen.rect([cx - 0.02 * h, by - 1.0 * h, cx + 0.02 * h, by - 0.89 * h], mix(AMBER, a))
    pen.rect([cx - 0.06 * h, by - 0.96 * h, cx + 0.06 * h, by - 0.93 * h], mix(AMBER, a))


def orbits(pen, t, a):
    for k, r in enumerate((440, 540, 650, 780)):
        col = mix(WHITE, 0.10 * a)
        pen.ell([CX - r, CY - r * 0.88, CX + r, CY + r * 0.88], outline=col, width=2)
        ang = t * (0.35 - 0.07 * k) + k * 1.7
        px, py = CX + r * math.cos(ang), CY + r * 0.88 * math.sin(ang)
        pen.ell([px - 7, py - 7, px + 7, py + 7], fill=mix(BLUE if k % 2 == 0 else AMBER, 0.85 * a))
    for k in range(48):
        ang = 2 * math.pi * k / 48
        r1, r2 = 800, 820 if k % 4 else 835
        pen.line((CX + r1 * math.cos(ang), CY + r1 * 0.88 * math.sin(ang)), (CX + r2 * math.cos(ang), CY + r2 * 0.88 * math.sin(ang)), mix(WHITE, 0.14 * a), 2)


def clock(pen, cx, cy, r, t, a):
    pen.ell([cx - r, cy - r, cx + r, cy + r], outline=mix(SILVER, 0.55 * a), width=3)
    for k in range(12):
        ang = 2 * math.pi * k / 12
        pen.line((cx + (r - 8) * math.cos(ang), cy + (r - 8) * math.sin(ang)), (cx + r * math.cos(ang), cy + r * math.sin(ang)), mix(SILVER, 0.5 * a), 2)
    am = t * 1.2
    pen.line((cx, cy), (cx + r * 0.75 * math.cos(am), cy + r * 0.75 * math.sin(am)), mix(AMBER, 0.8 * a), 3)
    pen.line((cx, cy), (cx + r * 0.45 * math.cos(am / 12), cy + r * 0.45 * math.sin(am / 12)), mix(WHITE, 0.7 * a), 4)


def hourglass(pen, cx, cy, s, t, a):
    c = mix(SILVER, 0.55 * a)
    pen.line((cx - s, cy - s * 1.4), (cx + s, cy - s * 1.4), c, 3)
    pen.line((cx - s, cy + s * 1.4), (cx + s, cy + s * 1.4), c, 3)
    pen.line((cx - s, cy - s * 1.4), (cx, cy), c, 3)
    pen.line((cx + s, cy - s * 1.4), (cx, cy), c, 3)
    pen.line((cx - s, cy + s * 1.4), (cx, cy), c, 3)
    pen.line((cx + s, cy + s * 1.4), (cx, cy), c, 3)
    k = (t * 0.25) % 1.0
    pen.poly([(cx - s * 0.7 * (1 - k), cy - s * 1.3 + s * 0.8 * k), (cx + s * 0.7 * (1 - k), cy - s * 1.3 + s * 0.8 * k), (cx, cy - 0.05 * s)], mix(AMBER, 0.7 * a))


def particles(pen, t):
    for k in range(18):
        bx = (k * 137) % W
        by = (k * 251) % H
        y = (by - t * (12 + k * 2.4)) % H
        x = bx + math.sin(t * 0.6 + k) * 26
        r = 4 + (k % 4) * 2
        c = mix(AMBER if k % 3 == 0 else BLUE, 0.35)
        pen.ell([x - r, y - r, x + r, y + r], fill=c)


def bounds(D):
    parts = [HOOK] + LINES + [CTA, QUESTION]
    total = float(sum(len(p) for p in parts))
    acc, out = 0.0, [0.0]
    for p in parts:
        acc += len(p)
        out.append(D * acc / total)
    return out


def frame(t, D, B):
    global BGIMG
    if BGIMG is None:
        BGIMG = make_bg()
    img = BGIMG.copy()
    pen = Pen(img)
    particles(pen, t)
    show = clamp(t / 0.8)
    orbits(pen, t, show)
    clock(pen, 150, 640, 62, t, show)
    hourglass(pen, 930, 640, 34, t, show)
    # mirror
    rx, ry = 300, 400
    glow = eio((t - B[1] * 0.6) / 1.2)
    pen.ell([CX - rx - 18, CY - ry - 18, CX + rx + 18, CY + ry + 18], fill=mix((40, 56, 90), 0.55 * show))
    pen.ell([CX - rx, CY - ry, CX + rx, CY + ry], fill=mix((6, 9, 18), show))
    pen.ell([CX - rx + 8, CY - ry + 8, CX + rx - 8, CY + ry - 8], fill=mix((70, 46, 14), 0.45 * glow))
    pen.ell([CX - rx - 8, CY - ry - 8, CX + rx + 8, CY + ry + 8], outline=mix(SILVER, show), width=12)
    # figures
    approach = eio((t - B[3]) / max(1.0, B[4] - B[3]))
    px = 250 + 150 * approach
    base = 1500
    pawn(pen, px, base, 270, show)
    pen.line((90, base + 6), (700, base + 6), mix(SILVER, 0.5 * show), 3)
    kingA = eio((t - B[1]) / 1.0)
    kx = CX + (CX - px) * 0.35
    kh = 360 + 90 * approach
    if kingA > 0.02:
        king(pen, kx, 1420, kh * (0.55 + 0.45 * kingA), kingA)
        pen.ell([kx - 170, 1000, kx + 170, 1340], outline=mix(AMBER, 0.35 * kingA * glow), width=3)
    tb = (t - B[4]) / 1.4
    if 0 < tb < 1:
        rr = 120 + 560 * eo(tb)
        pen.ell([CX - rr, CY - rr * 0.88, CX + rr, CY + rr * 0.88], outline=mix(AMBER, 1.0 - tb), width=6)
    f80, f56 = font(FB, 80), font(FB, 56)
    a = scene(t, -1, B[1] + 0.25)
    pill(pen, W / 2, 190, 'MOTIVATION', a)
    rich(pen, 320, HOOK, f80, WHITE, a, W - 160, 104, 1.0)
    b = scene(t, B[1] + 0.1, B[2] + 0.25)
    rich(pen, 300, LINES[0], f56, WHITE, b, W - 160, 76, eo((t - B[1] - 0.1) / 0.5))
    c = scene(t, B[2] - 0.1, B[3] + 0.25)
    rich(pen, 300, LINES[1], f56, WHITE, c, W - 160, 76, eo((t - B[2] + 0.1) / 0.5))
    g = scene(t, B[3] - 0.1, B[4] + 0.25)
    rich(pen, 300, LINES[2], f80, WHITE, g, W - 160, 104, eo((t - B[3] + 0.1) / 0.5))
    e = scene(t, B[4] - 0.1, B[5] + 0.15, 0.4)
    pill(pen, W / 2, 300, 'FOLLOW', e)
    if e > 0.02:
        pen.text((W / 2, 440), 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 52), mix(WHITE, e))
    q = scene(t, B[5] - 0.05, 999, 0.45)
    rich(pen, 300, QUESTION, f80, AMBER, q, W - 160, 108, eo((t - B[5]) / 0.5))
    pen.rect([0, 0, W * clamp(t / D), 8], mix(AMBER, 0.9))
    return img.resize((W, H), Image.LANCZOS)


def render(wav, out):
    D = duration(wav) + 0.7
    B = bounds(D - 0.7)
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(total):
        pr.stdin.write(frame(k / FPS, D, B).tobytes())
    pr.stdin.close()
    pr.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'narr':
        open('narration.txt', 'w').write(narration() + chr(10))
    else:
        render(sys.argv[2], sys.argv[3])
