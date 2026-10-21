import subprocess, sys, math, os
from PIL import Image, ImageDraw, ImageFont
from episodes import EPISODES, CTA

W, H, FPS = 1080, 1920, 24
BG = (10, 10, 15)
WHITE = (255, 255, 255)
BLUE = (45, 156, 255)
MUTED = (154, 164, 178)
RED = (255, 92, 92)
TRACK = (28, 36, 48)
COLORS = {'blue': BLUE, 'red': RED, 'muted': MUTED}
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def narration(ep):
    return ' '.join([ep['hook']] + ep['lines'] + [CTA, ep['question']])


def duration(wav):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav])
    return float(out.decode().strip())


def clamp(x):
    return max(0.0, min(1.0, x))


def scene(t, start, end, fade=0.35):
    return clamp((t - start) / fade) * clamp((end - t) / fade)


def mix(c, a):
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))


def center_text(d, y, text, f, color, a):
    if a <= 0.01:
        return
    d.text((W / 2, y), text, font=f, fill=mix(color, a), anchor='ma')


def wrap(d, text, f, maxw):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if d.textlength(test, font=f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def block(d, y, text, f, color, a, maxw, lead):
    for line in wrap(d, text, f, maxw):
        center_text(d, y, line, f, color, a)
        y += lead
    return y


def pill(d, cx, y, label, f, tc, bgc, a):
    if a <= 0.01:
        return
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([cx - tw / 2 - 36, y, cx + tw / 2 + 36, y + 84], radius=42, fill=mix(bgc, a))
    d.text((cx, y + 14), label, font=f, fill=mix(tc, a), anchor='ma')


def grid(d):
    for x in range(0, W, 120):
        d.line([x, 0, x, H], fill=(16, 18, 26), width=1)
    for y in range(0, H, 120):
        d.line([0, y, W, y], fill=(16, 18, 26), width=1)


def bars(d, items, g, a, base):
    n = len(items)
    gap = W / (n + 1)
    for i, it in enumerate(items):
        cx = gap * (i + 1)
        h = int(480 * it[1] * clamp(g * 1.2 - i * 0.15))
        col = COLORS[it[2]]
        if h > 4:
            d.rounded_rectangle([cx - 100, base - h, cx + 100, base], radius=24, fill=mix(col, a))
        d.text((cx, base + 24), it[0], font=font(FB, 38), fill=mix(col, a), anchor='ma')


def chain(d, labels, g, a, cy):
    n = len(labels)
    gap = W / (n + 1)
    for i, lab in enumerate(labels):
        k = clamp(g * n - i)
        cx = gap * (i + 1)
        if i > 0:
            px = gap * i
            d.line([px + 70, cy, px + (cx - px - 70) * k, cy], fill=mix(MUTED, a * k), width=8)
        r = int(70 * k)
        if r > 4:
            col = RED if i == n - 1 else BLUE
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(col, a))
        d.text((cx, cy + 100), lab, font=font(FB, 34), fill=mix(WHITE, a * k), anchor='ma')


def bounds(ep, D):
    parts = [ep['hook']] + ep['lines'] + [CTA, ep['question']]
    total = float(sum(len(p) for p in parts))
    acc, out = 0.0, [0.0]
    for p in parts:
        acc += len(p)
        out.append(D * acc / total)
    return out


def frame(t, D, ep, B):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    f80, f56, f48, f38 = font(FB, 80), font(FB, 56), font(FR, 50), font(FB, 38)
    nl = len(ep['lines'])
    # B indexes: 0 start, 1 end hook, 2.. lines, then CTA, then question
    a = scene(t, -1, B[1] + 0.2)
    pill(d, W / 2, 300, ep['label'], f38, BLUE, (15, 42, 69), a * clamp(t / 0.15))
    block(d, 520, ep['hook'], f80, WHITE, a * clamp(t / 0.15), W - 160, 108)
    b = scene(t, B[1] + 0.1, B[1 + nl] + 0.2)
    block(d, 300, ep['lines'][0], f48, MUTED, b * clamp((t - B[1] - 0.1) / 0.5), W - 180, 68)
    g = clamp((t - B[1] - 0.6) / max(0.8, (B[1 + nl] - B[1]) * 0.5))
    if ep['chart'][0] == 'bars':
        bars(d, ep['chart'][1], g, b, 1500)
    else:
        chain(d, ep['chart'][1], g, b, 1250)
    for k in range(1, nl):
        c = scene(t, B[1 + k] - 0.1, B[2 + k] + 0.1)
        block(d, 700, ep['lines'][k], f56, WHITE, c * clamp((t - B[1 + k]) / 0.4), W - 180, 80)
    e = scene(t, B[1 + nl] - 0.1, B[2 + nl] + 0.1, 0.35)
    pill(d, W / 2, 330, 'FOLLOW', f38, BLUE, (15, 42, 69), e)
    center_text(d, 470, 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 52), WHITE, e)
    f = scene(t, B[2 + nl] - 0.05, 999, 0.4)
    block(d, 800, ep['question'], f80, BLUE, f * clamp((t - B[2 + nl]) / 0.4), W - 160, 108)
    return img


def render(idx, wav, out):
    ep = EPISODES[idx - 1]
    D = duration(wav) + 0.7
    B = bounds(ep, D - 0.7)
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        p.stdin.write(frame(i / FPS, D, ep, B).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'narr':
        os.makedirs('out', exist_ok=True)
        for n, ep in enumerate(EPISODES, 1):
            open('out/narr_%02d.txt' % n, 'w').write(narration(ep) + chr(10))
    else:
        render(int(sys.argv[2]), sys.argv[3], sys.argv[4])
