import subprocess, os

BASE = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US'


def run(args, stdin_path=None):
    f = open(stdin_path) if stdin_path else None
    code = subprocess.run(args, stdin=f).returncode
    if f:
        f.close()
    return code


def get_voice(name):
    u = BASE + '/' + name + '/medium/en_US-' + name + '-medium.onnx'
    a = run(['curl', '-fL', '-o', 'voice.onnx', u])
    b = run(['curl', '-fL', '-o', 'voice.onnx.json', u + '.json'])
    return a == 0 and b == 0


os.makedirs('out', exist_ok=True)
run(['python', 'series.py', 'narr'])
voice = 'ryan'
ok = get_voice('ryan')
if not ok:
    voice = 'joe'
    ok = get_voice('joe')
engine = 'piper-' + voice
for n in range(1, 11):
    tag = '%02d' % n
    narr = 'out/narr_' + tag + '.txt'
    wav = 'out/v' + tag + '.wav'
    done = False
    if ok:
        done = run(['piper', '--model', 'voice.onnx', '--output_file', wav], narr) == 0
    if not done:
        run(['espeak-ng', '-s', '150', '-w', wav, '-f', narr])
        engine = 'espeak-fallback'
    run(['python', 'series.py', 'render', str(n), wav, 'out/ep' + tag + '.mp4'])
open('engine.txt', 'w').write(engine)
