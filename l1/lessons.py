import subprocess, sys, math
from PIL import Image
from lesson1 import W, H, FPS, S, BG, WHITE, BLUE, AMBER, MUTED, RED, FB, FR, CX, CY, PX0, PX1, PY0, PY1
from lesson1 import font, clamp, eo, eio, scene, mix, Pen, make_bg, wrap, pill, particles, duration

CTA = 'Follow INFINITYEXPLAINED for a new idea every day.'
COL = {'blue': BLUE, 'red': RED, 'amber': AMBER, 'muted': MUTED}

EP = {
    2: {'label': 'MEMORY',
        'parts': ['You can forget your homework, but never that embarrassing moment.',
                  'Why does your brain keep it?',
                  'Emotional events tend to be remembered more strongly, because brain regions like the amygdala help mark them as important.',
                  'Then we replay the memory, and each replay can strengthen it.',
                  'We also tend to overestimate how much others noticed, a bias called the spotlight effect.',
                  'Try this: when it replays, remind yourself it is just a memory, and refocus on the present.',
                  CTA, 'What memory do you replay the most?'],
        'keys': ['embarrassing', 'emotional', 'amygdala', 'replay', 'spotlight', 'memory', 'present'],
        'vis': [['net'], ['net'], ['chain', ['Embarrassing moment', 'Emotion alarm', 'Strong memory']], ['ring', 'REPLAY'],
                ['bars', [['Guess', 0.85, 'red'], ['Actual', 0.4, 'blue']]], ['ring', 'REFOCUS']]},
    3: {'label': 'SLEEP',
        'parts': ['Your body is resting. Your brain is working.',
                  'What is it doing all night?',
                  'During sleep, the brain cycles through stages, including deep sleep and REM sleep, roughly every ninety minutes.',
                  'Research suggests sleep helps stabilize new memories and clear waste products from the brain.',
                  'Missing sleep can make focus and mood harder to manage the next day.',
                  'Try this: keep a regular bedtime and dim your screens before sleep.',
                  CTA, 'What time will you go to bed tonight?'],
        'keys': ['working', 'ninety', 'memories', 'focus', 'mood', 'bedtime', 'sleep'],
        'vis': [['wave'], ['wave'], ['bars', [['Light', 0.5, 'blue'], ['Deep', 0.9, 'blue'], ['REM', 0.7, 'amber']]], ['link', 'SLEEP', 'MEMORY'],
                ['bars', [['Rested', 0.9, 'blue'], ['Tired', 0.4, 'red']]], ['ring', 'BEDTIME']]},
    4: {'label': 'MOTIVATION',
        'parts': ['Starting feels heavy. Continuing feels light.',
                  'Why is that?',
                  'Starting means facing effort and uncertainty all at once, so the brain tends to prefer comfortable options.',
                  'Once you begin, momentum can build, and the task feels more familiar and less threatening.',
                  'That is why tiny first steps, like two minutes, can work so well.',
                  'Try this: begin with the smallest version of the task.',
                  CTA, 'What is your smallest first step today?'],
        'keys': ['starting', 'heavy', 'light', 'momentum', 'tiny', 'two', 'smallest', 'step'],
        'vis': [['chain', ['Start', 'Momentum', 'Flow']], ['chain', ['Start', 'Momentum', 'Flow']], ['bars', [['Start', 0.9, 'red'], ['Later', 0.4, 'blue']]],
                ['chain', ['Begin', 'Familiar', 'Easier']], ['ring', '2 MIN'], ['ring', 'SMALL STEP']]},
    5: {'label': 'FOCUS',
        'parts': ['Multitasking is not doing two things at once.',
                  'So what is your brain really doing?',
                  'For tasks that need focus, it switches between them, and each switch costs time and attention.',
                  'Switching between tasks can slow you down and increase mistakes.',
                  'Doing one thing at a time lets attention settle and quality improve.',
                  'Try this: work in focused blocks of twenty five minutes, with notifications off.',
                  CTA, 'What will you focus on for the next twenty five minutes?'],
        'keys': ['multitasking', 'switches', 'costs', 'mistakes', 'attention', 'focused', 'twenty'],
        'vis': [['chain', ['Task A', 'Switch', 'Task B']], ['chain', ['Task A', 'Switch', 'Task B']], ['bars', [['Focused', 0.9, 'blue'], ['Switching', 0.5, 'red']]],
                ['bars', [['Mistakes', 0.8, 'red'], ['Speed', 0.4, 'blue']]], ['link', 'ONE TASK', 'QUALITY'], ['ring', '25 MIN']]},
    6: {'label': 'PROCRASTINATION',
        'parts': ['You know you should start. You still wait.',
                  'Why do we do that?',
                  'Psychologists find that procrastination is often about managing feelings, not managing time.',
                  'We avoid tasks that trigger stress, boredom or doubt, and the relief feels good right now.',
                  'But that relief can train the habit, and the stress often returns bigger.',
                  'Try this: name the feeling, then work for just five minutes.',
                  CTA, 'Which feeling stops you most often?'],
        'keys': ['procrastination', 'feelings', 'stress', 'relief', 'habit', 'feeling', 'five'],
        'vis': [['link', 'FEELING', 'AVOID'], ['link', 'FEELING', 'AVOID'], ['chain', ['Stress', 'Avoid', 'Relief']],
                ['bars', [['Relief now', 0.8, 'blue'], ['Stress later', 0.95, 'red']]], ['chain', ['Relief', 'Habit', 'Repeat']], ['ring', '5 MIN']]},
    7: {'label': 'STRESS',
        'parts': ['Stress starts in your brain before you notice it.',
                  'What happens first?',
                  'The brain detects a possible threat, and the body releases stress hormones such as adrenaline and cortisol.',
                  'Your heart rate rises and attention narrows, which helps you react fast.',
                  'Slow breathing, with longer exhales, can help calm the body alarm.',
                  'Try this: breathe in for four seconds and out for six, five times.',
                  CTA, 'When did you last feel your body relax?'],
        'keys': ['stress', 'brain', 'threat', 'hormones', 'heart', 'slow', 'breathing', 'four', 'six'],
        'vis': [['net'], ['net'], ['chain', ['Threat', 'Hormones', 'Alert']], ['bars', [['Calm', 0.35, 'blue'], ['Stressed', 0.9, 'red']]],
                ['pulse'], ['pulse']]},
    8: {'label': 'MUSIC',
        'parts': ['A few notes can change your whole mood.',
                  'How does that work?',
                  'Music engages brain regions linked to emotion, memory and reward.',
                  'Studies show that listening to music you enjoy can release dopamine, a chemical linked to reward.',
                  'Familiar songs can also bring back memories, which is why they feel so personal.',
                  'Try this: choose a song on purpose to match the mood you want.',
                  CTA, 'Which song changes your mood fastest?'],
        'keys': ['notes', 'mood', 'emotion', 'memory', 'reward', 'dopamine', 'songs', 'song'],
        'vis': [['wave'], ['wave'], ['net'], ['bars', [['Silence', 0.3, 'muted'], ['Music you enjoy', 0.8, 'amber']]],
                ['chain', ['Song', 'Memory', 'Feeling']], ['wave']]},
    9: {'label': 'LEARNING',
        'parts': ['Every time you learn, your brain physically changes.',
                  'What changes?',
                  'Neurons form and strengthen connections, called synapses, a process known as neuroplasticity.',
                  'Practice strengthens those connections, while connections that go unused can weaken.',
                  'Sleep and spaced practice help new learning stick.',
                  'Try this: review what you learned after one day, then after one week.',
                  CTA, 'What will you learn this week?'],
        'keys': ['learn', 'changes', 'connections', 'synapses', 'neuroplasticity', 'practice', 'sleep', 'review'],
        'vis': [['net'], ['net'], ['net'], ['bars', [['Practiced', 0.9, 'blue'], ['Unused', 0.3, 'red']]],
                ['chain', ['Practice', 'Sleep', 'Stick']], ['ring', 'DAY 1 AND WEEK 1']]},
    10: {'label': 'FIRST IMPRESSIONS',
         'parts': ['You decided about them in seconds.',
                   'Why do we trust first impressions?',
                   'The brain makes quick judgments from limited cues, which saves effort.',
                   'Research shows people form impressions within a fraction of a second, but these snap judgments are often not accurate.',
                   'The first impression then acts as an anchor, and we tend to look for evidence that agrees with it.',
                   'Try this: pause, and look for one thing that does not fit your first impression.',
                   CTA, 'When was your first impression wrong?'],
         'keys': ['seconds', 'quick', 'fraction', 'accurate', 'anchor', 'evidence', 'pause', 'impression'],
         'vis': [['bars', [['Fast', 0.95, 'amber'], ['Accurate', 0.4, 'blue']]], ['bars', [['Fast', 0.95, 'amber'], ['Accurate', 0.4, 'blue']]],
                 ['chain', ['Cue', 'Judgment', 'Done']], ['bars', [['Speed', 0.95, 'amber'], ['Accuracy', 0.4, 'blue']]],
                 ['chain', ['Anchor', 'Search', 'Agree']], ['ring', 'PAUSE']]},
}


def rich2(pen, y, text, f, base, a, maxw, lead, keys, slide=1.0):
    if a <= 0.02:
        return
    y = y + (1.0 - slide) * 34
    for line in wrap(pen, text, f, maxw):
        words = line.split(' ')
        total = pen.width(line, f)
        x = W / 2 - total / 2
        for wd in words:
            clean = wd.lower().strip('.,?!:')
            col = AMBER if clean in keys else base
            pen.text((x, y), wd, f, mix(col, a), anchor='la')
            x += pen.width(wd + ' ', f)
        y += lead


def v_bars(pen, items, p, a):
    n = len(items)
    gap = (PX1 - PX0) / float(n + 1)
    base = PY1 - 140
    for i, it in enumerate(items):
        cx = PX0 + gap * (i + 1)
        h = int(560 * it[1] * eio(p * 1.3 - i * 0.2))
        col = COL[it[2]]
        if h > 4:
            pen.rect([cx - 62, base - h, cx + 62, base], mix(col, a), r=18)
        pen.text((cx, base + 22), it[0], font(FB, 28), mix(col, a))
    pen.text((CX, PY1 - 56), 'ILLUSTRATION, NOT DATA', font(FB, 22), mix(MUTED, 0.7 * a))


def v_chain(pen, labels, p, a):
    n = len(labels)
    top, step = PY0 + 190, 230
    for i, lab in enumerate(labels):
        k = eio(p * n - i)
        cy = top + i * step
        if i > 0:
            pen.line((CX, cy - step + 70), (CX, cy - step + 70 + (step - 140) * k), mix(MUTED, a * k), 6)
        r = int(64 * k)
        if r > 4:
            pen.ell([CX - r, cy - r, CX + r, cy + r], fill=mix(RED if i == n - 1 else BLUE, a))
        if k > 0.2:
            pen.text((CX, cy + 82), lab, font(FB, 32), mix(WHITE, a * k))


def v_ring(pen, label, p, a):
    r = 170
    pen.ell([CX - r, CY - r, CX + r, CY + r], outline=mix((26, 34, 48), a), width=18)
    steps = 60
    cnt = int(steps * eio(p))
    for k in range(cnt):
        ang = -math.pi / 2 + 2 * math.pi * k / steps
        pen.ell([CX + r * math.cos(ang) - 9, CY + r * math.sin(ang) - 9, CX + r * math.cos(ang) + 9, CY + r * math.sin(ang) + 9], fill=mix(BLUE, a))
    words = label.split(' ')
    if len(words) > 2:
        pen.text((CX, CY - 40), ' '.join(words[:2]), font(FB, 40), mix(AMBER, a))
        pen.text((CX, CY + 10), ' '.join(words[2:]), font(FB, 40), mix(AMBER, a))
    else:
        pen.text((CX, CY - 32), label, font(FB, 52 if len(label) < 9 else 40), mix(AMBER, a))


def v_link(pen, l1, l2, p, a):
    r = 125
    sep = 150 - 80 * eio(p)
    pen.ell([CX - sep - r, CY - r, CX - sep + r, CY + r], outline=mix(BLUE, a), width=8)
    pen.ell([CX + sep - r, CY - r, CX + sep + r, CY + r], outline=mix(AMBER, a), width=8)
    pen.text((CX - 110, CY + r + 30), l1, font(FB, 28), mix(BLUE, a))
    pen.text((CX + 100, CY + r + 70), l2, font(FB, 28), mix(AMBER, a))


def v_wave(pen, t, a):
    n = 11
    gap = (PX1 - PX0 - 80) / float(n)
    for i in range(n):
        h = 120 + 260 * abs(math.sin(t * 2.2 + i * 0.7)) * (0.5 + 0.5 * math.sin(t * 0.6 + i))
        cx = PX0 + 60 + gap * i + gap / 2
        pen.rect([cx - 14, CY - h, cx + 14, CY + h], mix(AMBER if i % 3 == 0 else BLUE, a), r=14)


def v_net(pen, t, p, a):
    pts = []
    for k in range(13):
        ang = 2 * math.pi * k / 13 + 0.5 * math.sin(t * 0.4 + k)
        rr = 120 + (k % 4) * 60
        pts.append((CX + rr * math.cos(ang), CY + rr * math.sin(ang) * 1.2))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d2 = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if d2 < 230 and eio(p * 2.0 - (i + j) / 24.0) > 0.05:
                pen.line(pts[i], pts[j], mix(BLUE, 0.45 * a * eio(p * 2.0 - (i + j) / 24.0)), 3)
    for i, (x, y) in enumerate(pts):
        pulse = 0.5 + 0.5 * math.sin(t * 2.0 + i)
        r = 11 + 6 * pulse
        pen.ell([x - r, y - r, x + r, y + r], fill=mix(AMBER if i % 4 == 0 else BLUE, a))


def v_pulse(pen, t, a):
    cyc = 10.0
    ph = (t % cyc) / cyc
    if ph < 0.4:
        k = ph / 0.4
        word = 'IN'
    else:
        k = 1.0 - (ph - 0.4) / 0.6
        word = 'OUT'
    r = 90 + 130 * eio(k)
    pen.ell([CX - r, CY - r, CX + r, CY + r], fill=mix((20, 60, 110), a * 0.8), outline=mix(BLUE, a), width=6)
    pen.text((CX, CY - 40), word, font(FB, 72), mix(WHITE, a))


def draw_vis(pen, spec, t, t0, a):
    p = clamp((t - t0) / 3.0)
    kind = spec[0]
    if kind == 'bars':
        v_bars(pen, spec[1], p, a)
    elif kind == 'chain':
        v_chain(pen, spec[1], p, a)
    elif kind == 'ring':
        v_ring(pen, spec[1], clamp((t - t0) / 5.0), a)
    elif kind == 'link':
        v_link(pen, spec[1], spec[2], p, a)
    elif kind == 'wave':
        v_wave(pen, t, a)
    elif kind == 'net':
        v_net(pen, t, clamp((t - t0) / 4.0), a)
    elif kind == 'pulse':
        v_pulse(pen, t, a)


def bounds(parts, D):
    total = float(sum(len(x) for x in parts))
    acc, out = 0.0, [0.0]
    for x in parts:
        acc += len(x)
        out.append(D * acc / total)
    return out


BGIMG = None


def frame(t, D, B, ep):
    global BGIMG
    if BGIMG is None:
        BGIMG = make_bg()
    img = BGIMG.copy()
    pen = Pen(img)
    parts, keys, vis = ep['parts'], ep['keys'], ep['vis']
    particles(pen, t)
    show = clamp(t / 0.8)
    pen.rect([PX0 - 14, PY0 - 14, PX1 + 14, PY1 + 14], mix((40, 56, 90), 0.6 * show), r=70)
    pen.rect([PX0, PY0, PX1, PY1], mix((6, 9, 18), show), r=58)
    f50, f80 = font(FB, 50), font(FB, 80)
    for i in range(6):
        a = scene(t, B[i] - 0.1, B[i + 1] + 0.2, 0.4) if i > 0 else scene(t, -1, B[1] + 0.2, 0.4)
        if a > 0.02:
            same_prev = i > 0 and vis[i] == vis[i - 1]
            t0 = B[i - 1] if same_prev else B[i]
            draw_vis(pen, vis[i], t, t0, a)
    a0 = scene(t, -1, B[1] + 0.25)
    pill(pen, W / 2, 190, ep['label'], a0)
    rich2(pen, 310, parts[0], f80, WHITE, a0, W - 160, 100, keys, 1.0)
    q = scene(t, B[1] - 0.1, B[2] + 0.25)
    rich2(pen, 310, parts[1], f80, WHITE, q, W - 160, 100, keys, eo((t - B[1] + 0.1) / 0.5))
    for i in (2, 3, 4, 5):
        s = scene(t, B[i] - 0.1, B[i + 1] + 0.25)
        rich2(pen, 240, parts[i], f50, WHITE, s, W - 140, 66, keys, eo((t - B[i] + 0.1) / 0.5))
    e = scene(t, B[6] - 0.1, B[7] + 0.15, 0.4)
    pill(pen, W / 2, 300, 'FOLLOW', e)
    if e > 0.02:
        pen.text((W / 2, 440), 'INFINITYEXPLAINED  ' + chr(0x221E), font(FB, 52), mix(WHITE, e))
        pen.text((CX, CY), chr(0x221E), font(FB, 300), mix(BLUE, 0.9 * e))
    z = scene(t, B[7] - 0.05, 999, 0.45)
    rich2(pen, 300, parts[7], f80, AMBER, z, W - 160, 108, keys, eo((t - B[7]) / 0.5))
    if z > 0.02:
        pen.text((CX, CY), chr(0x221E), font(FB, 300), mix(BLUE, 0.9 * z))
    pen.rect([0, 0, W * clamp(t / D), 8], mix(AMBER, 0.9))
    return img.resize((W, H), Image.LANCZOS)


def render(n, wav, out):
    ep = EP[n]
    D = duration(wav) + 0.7
    B = bounds(ep['parts'], D - 0.7)
    total = int(D * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', str(W) + 'x' + str(H), '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-c:a', 'aac', '-b:a', '128k', '-af', 'apad', '-t', str(round(D, 3)), out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(total):
        pr.stdin.write(frame(k / FPS, D, B, ep).tobytes())
    pr.stdin.close()
    pr.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'narr':
        for n in EP:
            open('out/narr_%d.txt' % n, 'w').write(' '.join(EP[n]['parts']) + chr(10))
    else:
        render(int(sys.argv[2]), sys.argv[3], sys.argv[4])
