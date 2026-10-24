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
CX, CY = 540, 1230

PARTS = ['You open your phone for one minute. Then an hour disappears.',
         'What is happening inside your brain?',
         'Each swipe is a small surprise. You never know if the next video will be boring or amazing, and unpredictable rewards are especially good at keeping us coming back.',
         'Infinite scrolling also removes natural stopping points, so nothing tells you that is enough.',
         'Some studies link heavy short video use with more distraction, but they show a connection, not proof of cause.',
         'Try this: decide your stopping time before you start, and set a timer.',
         'Follow INFINITYEXPLAINED for a new idea every day.',
         'How long did your last scroll really last?']
KEYS = ['hour', 'swipe', 'surprise', 'unpredictable', 'stopping', 'timer', 'scroll', 'connection', 'proof', 'distraction']

FONTS = {}


def font(path, size):
    k = (path, size)
    if k not in FONTS:
        FONTS[k] = ImageFont.truetype(path, int(size * S))
    return FONTS[k]


def narration():
    return ' '.join(PARTS)


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
    total = float(sum(len(p) for p in PARTS))
    acc, out = 0.0, [0.0]
    for p in PARTS:
        acc += len(p)
        out.append(D * acc / total)
    return out


PX0, PX1, PY0, PY1 = 290, 790, 790, 1670
CARD_H, STEP = 300, 340
STEP_T, MOVE_T = 1.0, 0.4
RED = (255, 92, 92)


def card(pen, x0, y0, y1, k, a, amber):
    ytop = max(y0, PY0 + 24)
    ybot = min(y1, PY1 - 24)
    if ybot - ytop < 6:
        return
    col = AMBER if amber else (30, 78, 150) if k % 2 == 0 else (22, 48, 104)
    pen.rect([x0, ytop, x0 + 420, ybot], mix(col, a * (1.0 if amber else 0.85)), r=22 if (y0 >= PY0 + 24 and y1 <= PY1 - 24) else 0)
    if y0 >= PY0 + 24 and y1 <= PY1 - 24:
        pen.ell([x0 + 28, y0 + 28, x0 + 88, y0 + 88], fill=mix(WHITE, 0.85 * a))
        pen.rect([x0 + 110, y0 + 38, x0 + 340, y0 + 52], mix(WHITE, 0.55 * a), r=7)
        pen.rect([x0 + 110, y0 + 66, x0 + 290, y0 + 78], mix(WHITE, 0.35 * a), r=6)
        pen.rect([x0 + 28, y0 + 120, x0 + 392, y0 + 270], mix(WHITE, 0.14 * a), r=16)
        if amber:
            pen.text((x0 + 210, y0 + 150), '!', font(FB, 90), mix(WHITE, a))


def is_amber(i):
    return (i * 37) % 7 in (0, 3)


def flash_at(t, end_t):
    tt = min(t, end_t)
    idx = int(tt / STEP_T)
    e = eio((tt - idx * STEP_T) / MOVE_T)
    if is_amber(idx):
        return 1.0 - clamp(abs(e - 0.5) * 2)
    return 0.0


def feed(pen, t, a, end_t):
    tt = min(t, end_t)
    idx = int(tt / STEP_T)
    e = eio((tt - idx * STEP_T) / MOVE_T)
    for k in range(0, 4):
        y0 = PY0 + 24 + k * STEP - e * STEP
        card(pen, PX0 + 40, y0, y0 + CARD_H, idx + k, a, is_amber(idx + k))
    pen.rect([PX0 + 170, PY0 + 18, PX1 - 170, PY0 + 34], mix((6, 9, 18), a), r=8)


def nodes(pen, t, a, flash):
    for k in range(14):
        ang = 2 * math.pi * k / 14 + t * 0.15
        rx, ry = 430 + 40 * math.sin(t + k), 520 + 30 * math.cos(t * 0.7 + k)
        px, py = CX + rx * math.cos(ang), CY + ry * math.sin(ang)
        on = flash * (0.4 + 0.6 * ((k * 5) % 3) / 2.0)
        c = AMBER if on > 0.5 else BLUE
        pen.line((CX, CY), (px, py), mix(c, 0.10 + 0.25 * on) if a > 0 else BG, 2)
        pen.ell([px - 9 - 8 * on, py - 9 - 8 * on, px + 9 + 8 * on, py + 9 + 8 * on], fill=mix(c, (0.5 + 0.5 * on) * a))


def stop_line(pen, a):
    if a <= 0.02:
        return
    y = PY0 + 560
    for x in range(PX0 + 30, PX1 - 30, 40):
        pen.line((x, y), (x + 22, y), mix(RED, 0.85 * a), 5)
    pen.text((PX1 - 70, y - 70), 'X', font(FB, 64), mix(RED, a))


def link(pen, a, g):
    if a <= 0.02:
        return
    pen.rect([PX0, PY0, PX1, PY1], mix((6, 9, 18), a), r=58)
    r = 125
    sep = 150 - 80 * eio(g)
    pen.ell([CX - sep - r, CY - r, CX - sep + r, CY + r], outline=mix(BLUE, a), width=8)
    pen.ell([CX + sep - r, CY - r, CX + sep + r, CY + r], outline=mix(AMBER, a), width=8)
    pen.text((CX - 110, CY + r + 30), 'SCROLL', font(FB, 28), mix(BLUE, a))
    pen.text((CX + 100, CY + r + 70), 'DISTRACTION', font(FB, 28), mix(AMBER, a))
    pen.text((CX, CY - 20), 'link', font(FB, 56), mix(WHITE, a * eio(g)))
    pen.text((CX, CY + 50), 'not proof', font(FB, 44), mix(MUTED, a * eio(g)))


def timer_ring(pen, a, prog):
    if a <= 0.02:
        return
    pen.rect([PX0, PY0, PX1, PY1], mix((6, 9, 18), a), r=58)
    r = 170
    pen.ell([CX - r, CY - r, CX + r, CY + r], outline=mix((26, 34, 48), a), width=18)
    steps = 60
    n = int(steps * eio(prog))
    for k in range(n):
        ang = -math.pi / 2 + 2 * math.pi * k / steps
        x1, y1 = CX + r * math.cos(ang), CY + r * math.sin(ang)
        pen.ell([x1 - 9, y1 - 9, x1 + 9, y1 + 9], fill=mix(BLUE, a))
    pen.text((CX, CY - 40), 'SET A', font(FB, 52), mix(WHITE, a))
    pen.text((CX, CY + 20), 'TIMER', font(FB, 64), mix(AMBER, a))


def frame(t, D, B):
    global BGIMG
    if BGIMG is None:
        BGIMG = make_bg()
    img = BGIMG.copy()
    pen = Pen(img)
    particles(pen, t)
    show = clamp(t / 0.8)
    f50, f80 = font(FB, 50), font(FB, 80)
    scroll_end = B[4]
    in_cards = scene(t, -1, B[4] - 0.1, 0.4)
    nodes(pen, t, show, flash_at(t, scroll_end) * in_cards)
    pen.rect([PX0 - 14, PY0 - 14, PX1 + 14, PY1 + 14], mix((40, 56, 90), 0.6 * show), r=70)
    pen.rect([PX0, PY0, PX1, PY1], mix((6, 9, 18), show), r=58)
    if in_cards > 0.02:
        feed(pen, t, in_cards, scroll_end)
    if t > B[3] and t < B[4]:
        stop_line(pen, scene(t, B[3], B[4] - 0.1, 0.4))
    link(pen, scene(t, B[4] - 0.1, B[5] + 0.1, 0.4), clamp((t - B[4]) / 1.2))
    timer_ring(pen, scene(t, B[5] - 0.1, B[6] + 0.2, 0.4), clamp((t - B[5]) / max(1.0, B[6] - B[5])))
    cnt = scene(t, -1, B[2] + 0.2, 0.4)
    if cnt > 0.02:
        m = int(1 + 59 * eio((t - 0.6) / max(1.0, B[1] - 0.6)))
        pen.text((W / 2, 1720), str(m) + ' MIN', font(FB, 72), mix(AMBER, cnt))
    a = scene(t, -1, B[1] + 0.25)
    pill(pen, W / 2, 190, 'BRAIN AND PHONE', a)
    rich(pen, 310, PARTS[0], f80, WHITE, a, W - 160, 100, 1.0)
    q = scene(t, B[1] - 0.1, B[2] + 0.25)
    rich(pen, 310, PARTS[1], f80, WHITE, q, W - 160, 100, eo((t - B[1] + 0.1) / 0.5))
    for i in (2, 3, 4, 5):
        s = scene(t, B[i] - 0.1, B[i + 1] + 0.25)
        rich(pen, 240, PARTS[i], f50, WHITE, s, W - 140, 66, eo((t - B[i] + 0.1) / 0.5))
    e = scene(t, B[6] - 0.1, B[7] + 0.15, 0.4)
    pill(pen, W / 2, 300, 'FOLLOW', e)
    if e > 0.02:
        pen.text((W / 2, 440), 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 52), mix(WHITE, e))
    z = scene(t, B[7] - 0.05, 999, 0.45)
    rich(pen, 300, PARTS[7], f80, AMBER, z, W - 160, 108, eo((t - B[7]) / 0.5))
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
