import sys, subprocess, math, json, base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL import features

try:
    if features.check('raqm'):
        raise ImportError('raqm handles Arabic')
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(s):
        return get_display(arabic_reshaper.reshape(s))
except Exception:
    def ar(s):
        return s

W, H, FPS, S = 1080, 1920, 24, 2
BG = (9, 14, 28)
WHITE = (255, 255, 255)
BLUE = (45, 156, 255)
AMBER = (245, 165, 36)
MUTED = (170, 180, 195)
SOFT = (255, 214, 140)
RED = (255, 92, 92)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CX, CY = 540, 1220
COL = {'blue': BLUE, 'red': RED, 'amber': AMBER, 'muted': MUTED}
AR_B64 = 'eyJpbXAiOnsiaG9vayI6Itiq2LTYudixINij2YbZgyDZhdit2KrYp9mE2J8g2YPYq9mK2LHZiNmGINmK2LTYudix2YjZhiDZhdir2YTZgy4iLCJsMSI6ItmK2LPZhdmK2YfYpyDYudmE2YXYp9ihINin2YTZhtmB2LMgwqvYuNin2YfYsdipINin2YTZhdit2KrYp9mEwrs6INin2YTYtNmDINmB2Yog2YbYrNin2K3ZgyDYsdi62YUg2YjYrNmI2K8g2KPYr9mE2Kkg2K3ZgtmK2YLZitipLiIsImwyIjoi2YfZiiDYtNin2KbYudipINit2KrZiSDYqNmK2YYg2KfZhNmF2KrZgdmI2YLZitmG2Iwg2YjZhNmK2LPYqiDYqti02K7Ziti12YvYpyDYt9io2YrZi9inLiIsImwzIjoi2KzYsdmR2Kgg2YfYsNinOiDYp9mD2KrYqCDYq9mE2KfYqyDZhtiq2KfYptisINit2YLZitmC2YrYqSDYrdmC2YLYqtmH2KcuIiwiY3RhIjoi2KrYp9io2LkgSU5GSU5JVFlFWFBMQUlORUQg2YTZhdiy2YrYryDZhdmGINin2YTYo9mB2YPYp9ixLiIsInEiOiLZhdiq2Ykg2LTZg9mD2Kog2YHZiiDZhtmB2LPZgyDYo9mD2KvYsdifIn0sIndhbmRlciI6eyJob29rIjoi2LnZgtmE2YMg2YrYtNix2K8g2YHZiiDZhti12YEg2YrZiNmF2YMg2KrZgtix2YrYqNmL2KcuIiwibDEiOiLZiNis2K/YqiDYr9ix2KfYs9ipINmD2KjZitix2Kkg2KPZhiDYp9mE2YbYp9izINmK2LTYsdiv2YjZhiDZgdmKINmF2Kcg2YrZgtin2LHYqCDZhti12YEg2YTYrdi42KfYqiDZitmC2LjYqtmH2YUuIiwibDIiOiLYp9mE2LTYsdmI2K8g2YLYryDZiti62LDZkdmKINin2YTYpdio2K/Yp9i52Iwg2YTZg9mG2Ycg2YLYryDZitio2LnYr9mDINi52YYg2KfZhNmF2YfZhdipLiIsImwzIjoi2KzYsdmR2Kgg2YfYsNinOiDYrdmK2YYg2KrZhNin2K3YuNmH2Iwg2LnZj9ivINio2YfYr9mI2KEg2KXZhNmJINi02YrYoSDZiNin2K3Yry4iLCJjdGEiOiLYqtin2KjYuSBJTkZJTklUWUVYUExBSU5FRCDZhNmF2LLZitivINmF2YYg2KfZhNij2YHZg9in2LEuIiwicSI6Itil2YTZiSDYo9mK2YYg2LTYsdivINi52YLZhNmDINmE2YTYqtmI2J8ifSwibmFtZXMiOnsiaG9vayI6ItmG2LPZitiqINin2LPZhdmHINiu2YTYp9mEINir2YjYp9mG2Y0uIiwibDEiOiLYutin2YTYqNmL2Kcg2YTZhSDZitmP2K3Zgdi4INin2YTYp9iz2YUg2KPYtdmE2YvYp9iMINmE2KPZhiDYp9mG2KrYqNin2YfZgyDZg9in2YYg2YHZiiDZhdmD2KfZhiDYotiu2LEg2K3ZitmGINiz2YXYudiq2YcuIiwibDIiOiLYqtmD2LHYp9ix2Ycg2KjYtdmI2Kog2LnYp9mE2Y0g2YjYsdio2LfZhyDYqNi12YjYsdipINmC2K8g2YrYs9in2LnYr9in2YYuIiwibDMiOiLYrNix2ZHYqCDZh9iw2Kc6INmC2YQg2KfYs9mF2Ycg2YXYsdipINmI2KfYrdiv2Kkg2YHZiiDYsdiv2ZHZgy4iLCJjdGEiOiLYqtin2KjYuSBJTkZJTklUWUVYUExBSU5FRCDZhNmF2LLZitivINmF2YYg2KfZhNij2YHZg9in2LEuIiwicSI6ItmH2YQg2KrYqtiw2YPYsSDYotiu2LEg2KfYs9mFINiz2YXYudiq2YfYnyJ9fQ=='
AR_TXT = json.loads(base64.b64decode(AR_B64).decode('utf-8'))
CTA = 'Follow INFINITYEXPLAINED for more.'

EP = {
    'imp': {'label': 'IMPOSTOR FEELINGS',
            'en': ['Feel like a fraud? Many people do.',
                   'Psychologists call it the impostor phenomenon: doubting your success despite real evidence.',
                   'It is common, even among high achievers, and it is not a diagnosis.',
                   'Try this: write down three real results you earned.',
                   CTA, 'When did you doubt yourself most?'],
            'keys': ['fraud', 'impostor', 'evidence', 'common', 'diagnosis', 'three', 'results'],
            'vis': [['bars', [['Doubt', 0.9, 'red'], ['Evidence', 0.55, 'blue']]], ['link', 'DOUBT', 'EVIDENCE'], ['net'],
                    ['chain', ['Result 1', 'Result 2', 'Result 3']], ['logo'], ['logo']]},
    'wander': {'label': 'MIND WANDERING',
               'en': ['Your mind wanders half your day.',
                      'One large study found people mind wander in almost half of their waking moments.',
                      'Wandering can fuel creativity, but it can also pull you away from the task.',
                      'Try this: when you notice it, gently return to one thing.',
                      CTA, 'Where did your mind just go?'],
               'keys': ['wanders', 'half', 'study', 'creativity', 'task', 'gently', 'return'],
               'vis': [['wave'], ['bars', [['Task', 0.53, 'blue'], ['Wandering', 0.47, 'amber']]], ['net'],
                       ['ring', 'RETURN'], ['logo'], ['logo']]},
    'names': {'label': 'MEMORY FOR NAMES',
              'en': ['You forgot their name in seconds.',
                     'Often the name was never stored, because your attention was elsewhere when you heard it.',
                     'Repeating it out loud and linking it to an image can help.',
                     'Try this: say their name once in your reply.',
                     CTA, 'Can you remember the last name you heard?'],
              'keys': ['forgot', 'seconds', 'never', 'attention', 'repeating', 'image', 'name'],
              'vis': [['chain', ['Hear', 'Attention?', 'Store']], ['link', 'ATTENTION', 'MEMORY'], ['chain', ['Repeat', 'Image', 'Remember']],
                      ['ring', 'SAY IT ONCE'], ['logo'], ['logo']]},
}

FONTS = {}


def font(size):
    if size not in FONTS:
        FONTS[size] = ImageFont.truetype(FB, int(size * S))
    return FONTS[size]


def clamp(x):
    return max(0.0, min(1.0, x))


def eo(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def scene(t, start, end, fade=0.2):
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

    def text(self, xy, s, f, fill, anchor='ma'):
        self.d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill, anchor=anchor)

    def width(self, s, f):
        return self.d.textlength(s, font=f) / S


def make_bg():
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    seed = 12345
    pal = [(14, 26, 62), (22, 48, 104), (10, 18, 44), (30, 78, 150), (40, 110, 190), (70, 60, 40)]
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
            c = pal[int(jit * 5.99)]
        ln = 20 + jit * 22
        d.line([x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln], fill=c, width=int(7 + jit * 6))
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    img = Image.blend(Image.new('RGB', (W, H), BG), img, 0.62)
    shade = Image.new('L', (1, H))
    px = shade.load()
    for y in range(H):
        px[0, y] = int(255 * (0.28 + 0.72 * eio((y / float(H) - 0.12) / 0.5)))
    img = Image.composite(img, Image.new('RGB', (W, H), BG), shade.resize((W, H)))
    return img.resize((W * S, H * S), Image.LANCZOS)


def wrap(pen, text, f, maxw):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if pen.width(ar(test) if any(ord(c) > 1500 for c in test) else test, f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def en_block(pen, y, text, size, t, t0, t1, keys, a, lead, instant=False):
    f = font(size)
    lines = wrap(pen, text, f, W - 140)
    total = float(len(text))
    cum = 0
    for line in lines:
        words = line.split(' ')
        x = W / 2 - pen.width(line, f) / 2
        for wd in words:
            start = t0 + (cum / total) * (t1 - t0) * 0.92
            k = 1.0 if instant else eo((t - start) / 0.18)
            clean = wd.lower().strip('.,?!:')
            hot = (not instant) and (t - start) < 0.3 and k > 0
            col = AMBER if (clean in keys or hot) else WHITE
            if k > 0.02:
                pen.text((x, y + (1 - k) * 18), wd, f, mix(col, a * k), anchor='la')
            x += pen.width(wd + ' ', f)
            cum += len(wd) + 1
        y += lead
    return y


def ar_block(pen, y, text, size, a, lead):
    f = font(size)
    lines = wrap(pen, text, f, W - 160)
    for line in lines:
        pen.text((W / 2, y), ar(line), f, mix(SOFT, a))
        y += lead
    return y


def v_bars(pen, items, p, a):
    n = len(items)
    gap = 760.0 / (n + 1)
    base = 1640
    for i, it in enumerate(items):
        cx = 160 + gap * (i + 1)
        h = int(560 * it[1] * eo(p * 1.4 - i * 0.2))
        col = COL[it[2]]
        if h > 4:
            pen.rect([cx - 70, base - h, cx + 70, base], mix(col, a), r=20)
        pen.text((cx, base + 24), it[0], font(30), mix(col, a))
    pen.text((CX, 1745), 'ILLUSTRATION, NOT DATA', font(22), mix(MUTED, 0.7 * a))


def v_chain(pen, labels, p, a):
    n = len(labels)
    for i, lab in enumerate(labels):
        k = eo(p * n - i)
        cy = 960 + i * 250
        if i > 0:
            pen.line((CX, cy - 250 + 70), (CX, cy - 250 + 70 + 110 * k), mix(MUTED, a * k), 6)
        r = int(70 * k)
        if r > 4:
            pen.ell([CX - r, cy - r, CX + r, cy + r], fill=mix(RED if i == n - 1 else BLUE, a))
        if k > 0.2:
            pen.text((CX, cy + 84), lab, font(34), mix(WHITE, a * k))


def v_ring(pen, label, p, a):
    r = 180
    pen.ell([CX - r, CY - r, CX + r, CY + r], outline=mix((26, 34, 48), a), width=18)
    for k in range(int(60 * eio(p))):
        ang = -math.pi / 2 + 2 * math.pi * k / 60
        pen.ell([CX + r * math.cos(ang) - 10, CY + r * math.sin(ang) - 10, CX + r * math.cos(ang) + 10, CY + r * math.sin(ang) + 10], fill=mix(BLUE, a))
    pen.text((CX, CY - 34), label, font(48 if len(label) < 8 else 38), mix(AMBER, a))


def v_link(pen, l1, l2, p, a):
    r = 140
    sep = 170 - 90 * eio(p)
    pen.ell([CX - sep - r, CY - r, CX - sep + r, CY + r], outline=mix(BLUE, a), width=9)
    pen.ell([CX + sep - r, CY - r, CX + sep + r, CY + r], outline=mix(AMBER, a), width=9)
    pen.text((CX - 120, CY + r + 34), l1, font(30), mix(BLUE, a))
    pen.text((CX + 110, CY + r + 76), l2, font(30), mix(AMBER, a))


def v_wave(pen, t, a):
    n = 13
    for i in range(n):
        h = 110 + 280 * abs(math.sin(t * 2.4 + i * 0.7)) * (0.5 + 0.5 * math.sin(t * 0.6 + i))
        cx = 150 + 65 * i
        pen.rect([cx - 15, CY - h, cx + 15, CY + h], mix(AMBER if i % 3 == 0 else BLUE, a), r=15)


def v_net(pen, t, p, a):
    pts = []
    for k in range(13):
        ang = 2 * math.pi * k / 13 + 0.5 * math.sin(t * 0.4 + k)
        rr = 130 + (k % 4) * 70
        pts.append((CX + rr * math.cos(ang), CY + rr * math.sin(ang) * 1.15))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d2 = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            e = eio(p * 2.0 - (i + j) / 24.0)
            if d2 < 250 and e > 0.05:
                pen.line(pts[i], pts[j], mix(BLUE, 0.5 * a * e), 3)
    for i, (x, y) in enumerate(pts):
        r = 12 + 6 * (0.5 + 0.5 * math.sin(t * 2.0 + i))
        pen.ell([x - r, y - r, x + r, y + r], fill=mix(AMBER if i % 4 == 0 else BLUE, a))


def v_logo(pen, a, p):
    pen.text((CX, CY - 150), chr(0x221E), font(360 * (0.8 + 0.2 * eo(p))), mix(BLUE, 0.95 * a))


def draw_vis(pen, spec, t, t0, a):
    p = clamp((t - t0) / 1.6)
    k = spec[0]
    if k == 'bars':
        v_bars(pen, spec[1], p, a)
    elif k == 'chain':
        v_chain(pen, spec[1], p, a)
    elif k == 'ring':
        v_ring(pen, spec[1], clamp((t - t0) / 3.0), a)
    elif k == 'link':
        v_link(pen, spec[1], spec[2], p, a)
    elif k == 'wave':
        v_wave(pen, t, a)
    elif k == 'net':
        v_net(pen, t, clamp((t - t0) / 2.5), a)
    elif k == 'logo':
        v_logo(pen, a, p)


def particles(pen, t):
    for k in range(20):
        bx, by = (k * 137) % W, (k * 251) % H
        y = (by - t * (16 + k * 3.0)) % H
        x = bx + math.sin(t * 0.8 + k) * 30
        r = 4 + (k % 4) * 2
        pen.ell([x - r, y - r, x + r, y + r], fill=mix(AMBER if k % 3 == 0 else BLUE, 0.35))


def bounds(en, D):
    total = float(sum(len(x) for x in en))
    acc, out = 0.0, [0.0]
    for x in en:
        acc += len(x)
        out.append(D * acc / total)
    return out


BGIMG = None


def frame(t, D, B, key):
    global BGIMG
    if BGIMG is None:
        BGIMG = make_bg()
    ep, at = EP[key], AR_TXT[key]
    img = BGIMG.copy()
    pen = Pen(img)
    particles(pen, t)
    names = ['hook', 'l1', 'l2', 'l3', 'cta', 'q']
    bump = 0.0
    for i in range(6):
        t0, t1 = B[i], B[i + 1]
        a = scene(t, t0 - 0.05, t1 + 0.12, 0.18) if i > 0 else scene(t, -1, t1 + 0.12, 0.18)
        tau = t - t0
        if 0 <= tau < 0.6:
            rr = 90 + 760 * eo(tau / 0.6)
            pen.ell([CX - rr, CY - rr, CX + rr, CY + rr], outline=mix(AMBER, 0.55 * (1 - tau / 0.6)), width=4)
            bump += 0.02 * (1 - eio(tau / 0.5))
        if a <= 0.02:
            continue
        draw_vis(pen, ep['vis'][i], t, t0, a)
        slide = (1 - eo(tau / 0.3)) * 40 if tau >= 0 else 40
        if i == 0:
            y = en_block(pen, 220, ep['en'][0], 92, t, 0.0, t1, ep['keys'], a, 112, True)
            ar_block(pen, y + 20, at['hook'], 62, a, 84)
            pen.rect([CX - 90, 170, CX + 90, 176], mix(BLUE, a), r=3)
            pen.text((CX, 120), ep['label'], font(32), mix(BLUE, a))
        elif i < 4:
            y = en_block(pen, 220, ep['en'][i], 60, t, t0, t1, ep['keys'], a, 76)
            ar_block(pen, y + 16, at[names[i]], 50, a, 70)
        elif i == 4:
            pen.text((CX, 230), 'FOLLOW', font(58), mix(BLUE, a))
            pen.text((CX, 330), 'INFINITYEXPLAINED', font(52), mix(WHITE, a))
            ar_block(pen, 440, at['cta'], 50, a, 70)
        else:
            y = en_block(pen, 220, ep['en'][5], 84, t, t0, t1, [], a, 104)
            ar_block(pen, y + 20, at['q'], 62, a, 84)
    pen.rect([0, 0, W * clamp(t / D), 8], mix(AMBER, 0.9))
    z = 1.0 + 0.04 * eio(t / D) + bump
    bw, bh = W * S / z, H * S / z
    x0, y0 = (W * S - bw) / 2, (H * S - bh) / 2 + 30
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)


def duration(wav):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav])
    return float(out.decode().strip())


def render(key, wav, out):
    D = duration(wav) + 0.6
    B = bounds(EP[key]['en'], D - 0.6)
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(total):
        pr.stdin.write(frame(k / FPS, D, B, key).tobytes())
    pr.stdin.close()
    pr.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'narr':
        for k in EP:
            open('out/narr_%s.txt' % k, 'w').write(' '.join(EP[k]['en']) + chr(10))
    else:
        render(sys.argv[2], sys.argv[3], sys.argv[4])
