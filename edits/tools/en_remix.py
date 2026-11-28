"""Re-edit already-generated raw clips into a new English Reel with a distinct look and fresh file metadata.
Mirrored, slight zoom/regrade, grain, new captions, song timed so its drop lands on `drop_at`, metadata stripped.
python3 en_remix.py spec.json"""
import json, os, subprocess, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageFont
from hohohound_9 import render
from xmas_mums import line_w
sp = json.load(open(sys.argv[1])); TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/enr/"; os.makedirs(TMP, exist_ok=True)
segs = sp["segs"]; dur = sum(d for _, _, d in segs); ins = []; fc = []
for i, (clip, s, d) in enumerate(segs):
    ins += ["-ss", str(s), "-t", str(d), "-i", clip]
    fc.append(f"[{i}:v]fps=30,scale=1150:2044:force_original_aspect_ratio=increase,crop=1080:1920,hflip,setsar=1,setpts=PTS-STARTPTS[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,eq=contrast=1.03:saturation=1.06:gamma=0.98,colorbalance=rs=0.02:bs=-0.02,noise=alls=5:allf=t[v0]")
cur = "[v0]"; n = len(segs)
for j, (text, t0, t1) in enumerate(sp["text"]):
    lines = text.split("|"); t1 = dur + 1 if t1 == "end" else t1
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 48)
    while font.size > 34 and max(line_w(l, font) for l in lines) > 980:
        font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", font.size - 2)
    p = TMP + f"{sp['name']}_t{j}.png"; render(lines, p, font=font, stroke=3)
    ins += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
    fc.append(f"{cur}[{n + j}:v]overlay=0:{sp.get('ty', 400)}:enable='between(t\\,{t0}\\,{t1})'[o{j}]"); cur = f"[o{j}]"
fc.append(f"{cur}format=yuv420p[v]")
ai = n + len(sp["text"]); ss = max(0.0, sp["drop"] - sp["drop_at"])
ins += ["-ss", f"{ss:.2f}", "-t", f"{dur:.3f}", "-i", sp["song"]]
fc.append(f"[{ai}:a]afade=t=in:st=0:d=0.05,afade=t=out:st={dur - 0.9:.2f}:d=0.9,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
    "-map_metadata", "-1", "-map_chapters", "-1", "-metadata", f"creation_time={now}", "-metadata:s:v", "handler_name=VideoHandler", "-metadata:s:a", "handler_name=SoundHandler",
    "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M", "-r", "30", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", sp["out"]], capture_output=True, text=True)
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
print("OK", sp["out"], round(dur, 2))
