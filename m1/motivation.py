import subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
BG = (10, 10, 15)
WHITE = (255, 255, 255)
BLUE = (45, 156, 255)
MUTED = (154, 164, 178)
RED = (255, 92, 92)
TRACK = (28, 36, 48)
SKIN = (225, 232, 242)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

HOOK = 'You do not need motivation to start. You need to start to feel it.'
LINES = ['Research on behavior change suggests that a small action can build momentum.',
         'So begin with just two minutes.',
         'One tiny step is enough. Your future self is counting on today.']
CTA = 'Follow INFINITYEXPLAINED for a new idea every day.'
QUESTION = 'What is your two minute step today?'


def narration():
    return ' '.join([HOOK] + LINES + [CTA, QUESTION])


def font(path, size):
    return ImageFont.truetype(path, size)


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


STEP_W, STEP_H, X0, Y0, N = 150, 95, 110, 1560, 5


def step_top(i):
    return (X0 + i * STEP_W + STEP_W / 2, Y0 - i * STEP_H)


def stairs(d, a, lit):
    for i in range(N + 1):
        x = X0 + i * STEP_W
        top = Y0 - i * STEP_H
        col = BLUE if i <= lit else TRACK
        d.rectangle([x, top, x + STEP_W - 8, Y0 + 130], fill=mix(col, a * (0.9 if i <= lit else 0.8)))


def limb(d, p, q, color, w):
    d.line([p, q], fill=color, width=w)
    for pt in (p, q):
        d.ellipse([pt[0] - w / 2, pt[1] - w / 2, pt[0] + w / 2, pt[1] + w / 2], fill=color)


def figure(d, cx, fy, a, phase, arms_up):
    body = mix(BLUE, a)
    skin = mix(SKIN, a)
    sw = math.sin(phase)
    hip = (cx, fy - 90)
    shoulder_y = fy - 195
    lf = (cx - 24 + sw * 18, fy - max(0.0, sw) * 26)
    rf = (cx + 24 - sw * 18, fy - max(0.0, -sw) * 26)
    limb(d, (cx - 14, hip[1]), lf, body, 22)
    limb(d, (cx + 14, hip[1]), rf, body, 22)
    d.rounded_rectangle([cx - 36, shoulder_y - 8, cx + 36, fy - 80], radius=26, fill=body)
    if arms_up > 0.01:
        hl = (cx - 40 - 40 * arms_up, shoulder_y - 40 - 70 * arms_up)
        hr = (cx + 40 + 40 * arms_up, shoulder_y - 40 - 70 * arms_up)
    else:
        hl = (cx - 56, fy - 120 + sw * 14)
        hr = (cx + 56, fy - 120 - sw * 14)
    limb(d, (cx - 34, shoulder_y + 6), hl, skin, 16)
    limb(d, (cx + 34, shoulder_y + 6), hr, skin, 16)
    d.ellipse([cx - 40, shoulder_y - 92, cx + 40, shoulder_y - 12], fill=skin)


def climb_pos(p):
    s = clamp(p) * N
    i = min(int(s), N - 1) if s < N else N - 1
    f = s - i if s < N else 1.0
    a, b = step_top(i), step_top(i + 1)
    x = a[0] + (b[0] - a[0]) * f
    y = a[1] + (b[1] - a[1]) * f - math.sin(math.pi * f) * 45
    return x, y, i, f


def ring(d, cx, cy, r, prog, a):
    if a <= 0.01:
        return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=mix(TRACK, a), width=18)
    d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * prog, fill=mix(BLUE, a), width=18)


def bounds(D):
    parts = [HOOK] + LINES + [CTA, QUESTION]
    total = float(sum(len(p) for p in parts))
    acc, out = 0.0, [0.0]
    for p in parts:
        acc += len(p)
        out.append(D * acc / total)
    return out


def frame(t, D, B):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    f80, f56, f48, f38 = font(FB, 80), font(FB, 56), font(FR, 50), font(FB, 38)
    # B: 0 start, 1 end hook, 2 end line1, 3 end line2, 4 end line3, 5 end cta, 6 end question
    climb_start, climb_end = B[1], B[4]
    p = clamp((t - climb_start) / max(0.5, climb_end - climb_start))
    x, y, i, f = climb_pos(p)
    show_fig = scene(t, -1, B[4] + 0.4, 0.3)
    stairs(d, show_fig, i + (1 if f > 0.5 else 0))
    if t < climb_start:
        fx, fy = step_top(0)
        ph = 0.0
    else:
        fx, fy = x, y
        ph = t * 9.0 if p < 1.0 else 0.0
    up = clamp((t - B[3]) / 0.6) if p >= 1.0 or t > B[3] else 0.0
    figure(d, fx, fy, show_fig, ph, up)
    a = scene(t, -1, B[1] + 0.2)
    pill(d, W / 2, 230, 'MOTIVATION', f38, BLUE, (15, 42, 69), a)
    block(d, 380, HOOK, f80, WHITE, a, W - 160, 104)
    b = scene(t, B[1] + 0.1, B[2] + 0.2)
    block(d, 330, LINES[0], f56, MUTED, b, W - 160, 76)
    c = scene(t, B[2] - 0.1, B[3] + 0.2)
    block(d, 330, LINES[1], f80, WHITE, c, W - 160, 104)
    ring(d, W / 2, 800, 170, clamp((t - B[2]) / max(0.5, B[3] - B[2])), c)
    center_text(d, 760, '2 MIN', font(FB, 64), BLUE, c * clamp((t - B[2]) / 0.4))
    g = scene(t, B[3] - 0.1, B[4] + 0.2)
    block(d, 330, LINES[2], f56, WHITE, g, W - 160, 76)
    e = scene(t, B[4] - 0.1, B[5] + 0.1, 0.35)
    pill(d, W / 2, 330, 'FOLLOW', f38, BLUE, (15, 42, 69), e)
    center_text(d, 470, 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 52), WHITE, e)
    q = scene(t, B[5] - 0.05, 999, 0.4)
    block(d, 800, QUESTION, f80, BLUE, q * clamp((t - B[5]) / 0.4), W - 160, 108)
    return img


def render(wav, out):
    D = duration(wav) + 0.7
    B = bounds(D - 0.7)
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
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
