import subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
BG = (10, 10, 15)
WHITE = (255, 255, 255)
BLUE = (45, 156, 255)
MUTED = (154, 164, 178)
RED = (255, 92, 92)
TRACK = (28, 36, 48)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def duration(wav):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav])
    return float(out.decode().strip())


def alpha(t, start, dur=0.5):
    return max(0.0, min(1.0, (t - start) / dur))


def mix(c, a):
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))


def center_text(d, y, text, f, color, a):
    if a <= 0:
        return
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W - (box[2] - box[0])) / 2, y), text, font=f, fill=mix(color, a))


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


def bar(d, y, progress, a, color):
    if a <= 0:
        return
    x0, x1, h = 190, W - 190, 30
    d.rounded_rectangle([x0, y, x1, y + h], radius=15, fill=mix(TRACK, a))
    w = int((x1 - x0) * progress)
    if w > 4:
        d.rounded_rectangle([x0, y, x0 + w, y + h], radius=15, fill=mix(color, a))


def pill(d, cx, y, label, f, tc, bgc, a):
    if a <= 0:
        return
    tw = d.textlength(label, font=f)
    x0, x1 = cx - tw / 2 - 36, cx + tw / 2 + 36
    d.rounded_rectangle([x0, y, x1, y + 84], radius=42, fill=mix(bgc, a))
    d.text((cx - tw / 2, y + 14), label, font=f, fill=mix(tc, a))


def grid(d):
    for x in range(0, W, 120):
        d.line([x, 0, x, H], fill=(16, 18, 26), width=1)
    for y in range(0, H, 120):
        d.line([0, y, W, y], fill=(16, 18, 26), width=1)


def frame(t, D):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    s = lambda f: f * D
    fb60, fb70, fr44 = font(FB, 60), font(FB, 70), font(FR, 44)
    pill(d, W / 2, 330, 'MYTH VS SCIENCE', font(FB, 38), BLUE, (15, 42, 69), alpha(t, 0, 0.5))
    y = 460
    for line in wrap(d, 'You only use 10% of your brain.', fb70, W - 200):
        center_text(d, y, line, fb70, WHITE, alpha(t, s(0.02), 0.6))
        y += 92
    p1 = min(0.1, 0.1 * alpha(t, s(0.08), s(0.07)))
    bar(d, 700, p1, alpha(t, s(0.06), 0.4), BLUE)
    pill(d, W / 2, 800, 'FALSE', fb60, RED, (58, 21, 24), alpha(t, s(0.16), 0.3))
    y = 960
    for line in wrap(d, 'Brain scans show activity across the whole brain, even during sleep.', fr44, W - 220):
        center_text(d, y, line, fr44, MUTED, alpha(t, s(0.24), 0.6))
        y += 62
    bar(d, 1110, alpha(t, s(0.28), s(0.17)), alpha(t, s(0.27), 0.4), WHITE)
    center_text(d, 1200, 'Different tasks light up different regions.', fr44, MUTED, alpha(t, s(0.46), 0.6))
    for i, lab in enumerate(['Speaking', 'Seeing', 'Moving']):
        pill(d, 250 + i * 290, 1290, lab, font(FB, 36), BLUE, (15, 42, 69), alpha(t, s(0.50) + i * 0.4, 0.4))
    center_text(d, 1450, 'NEARLY ALL', font(FB, 130), BLUE, alpha(t, s(0.64), 0.5))
    center_text(d, 1670, 'of your brain is used over a single day.', fr44, MUTED, alpha(t, s(0.76), 0.6))
    center_text(d, 1740, 'MYTH BUSTED', font(FB, 64), BLUE, alpha(t, s(0.88), 0.6))
    center_text(d, 1830, 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 34), MUTED, alpha(t, s(0.93), 0.6))
    return img


def main(wav, out):
    D = duration(wav) + 0.6
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        p.stdin.write(frame(i / FPS, D).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
