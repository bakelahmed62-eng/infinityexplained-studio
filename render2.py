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


def clamp(x):
    return max(0.0, min(1.0, x))


def scene(t, start, end, fade=0.4):
    return clamp((t - start) / fade) * clamp((end - t) / fade)


def mix(c, a):
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))


def center_text(d, y, text, f, color, a):
    if a <= 0.01:
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
    d.text((cx - tw / 2, y + 14), label, font=f, fill=mix(tc, a))


def grid(d):
    for x in range(0, W, 120):
        d.line([x, 0, x, H], fill=(16, 18, 26), width=1)
    for y in range(0, H, 120):
        d.line([0, y, W, y], fill=(16, 18, 26), width=1)


def vbar(d, cx, base, height, color, a):
    if height < 4 or a <= 0.01:
        return
    d.rounded_rectangle([cx - 110, base - height, cx + 110, base], radius=24, fill=mix(color, a))


def replay_ring(d, cx, cy, r, prog, a):
    if a <= 0.01:
        return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=mix(TRACK, a), width=16)
    end = -90 + 330 * prog
    d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=end, fill=mix(RED, a), width=16)
    ang = math.radians(end)
    px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
    d.ellipse([px - 30, py - 30, px + 30, py + 30], fill=mix(RED, a))
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=mix(BLUE, a))


def frame(t, D):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    s = lambda f: f * D
    f70, f44, f38 = font(FB, 70), font(FR, 44), font(FB, 38)
    # Scene A
    a = scene(t, -1, s(0.42))
    pill(d, W / 2, 250, 'PSYCHOLOGY', f38, BLUE, (15, 42, 69), a * clamp(t / 0.5))
    block(d, 380, 'Why do bad moments stay with you?', f70, WHITE, a * clamp((t - 0.2) / 0.6), W - 180, 92)
    pill(d, W / 2, 720, 'NEGATIVITY BIAS', f38, RED, (58, 21, 24), a * clamp((t - s(0.14)) / 0.4))
    block(d, 850, 'Bad moments tend to grab more attention than good ones.', f44, MUTED, a * clamp((t - s(0.2)) / 0.5), W - 220, 62)
    g = clamp((t - s(0.24)) / (s(0.12)))
    vbar(d, 330, 1560, int(430 * g), RED, a)
    vbar(d, 750, 1560, int(190 * g), BLUE, a)
    d.text((330, 1590), 'Bad', font=font(FB, 40), fill=mix(RED, a * g), anchor='ma')
    d.text((750, 1590), 'Good', font=font(FB, 40), fill=mix(BLUE, a * g), anchor='ma')
    # Scene B
    b = scene(t, s(0.42), s(0.72))
    block(d, 420, 'Replaying them keeps the memory fresh.', f70, WHITE, b, W - 180, 92)
    replay_ring(d, W / 2, 1000, 230, clamp((t - s(0.46)) / s(0.2)), b)
    center_text(d, 1350, 'Again. And again.', f44, MUTED, b * clamp((t - s(0.52)) / 0.5))
    # Scene C
    c = scene(t, s(0.72), 99, 0.5)
    pill(d, W / 2, 420, 'TRY THIS', f38, BLUE, (15, 42, 69), c)
    block(d, 580, 'Name one thing that went well today.', f70, WHITE, c * clamp((t - s(0.74)) / 0.6), W - 180, 92)
    center_text(d, 1000, 'Notice the good', font(FB, 76), BLUE, c * clamp((t - s(0.86)) / 0.6))
    center_text(d, 1100, 'on purpose.', font(FB, 76), BLUE, c * clamp((t - s(0.86)) / 0.6))
    center_text(d, 1760, 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 34), MUTED, c * clamp((t - s(0.92)) / 0.6))
    return img


def main(wav, out):
    D = duration(wav) + 0.8
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total):
        p.stdin.write(frame(i / FPS, D).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
