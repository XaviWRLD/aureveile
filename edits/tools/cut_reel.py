"""Cut a multi-shot generation into a tight Reel: pick segments, phone-look finish, timed captions, silent output (add an in-app sound).
python3 cut_reel.py src.mp4 out.mp4 "a-b,c-d,..." "text|line2@t0@t1;text2@t0@t1" [text_y]"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageFont
from hohohound_9 import render
from xmas_mums import line_w
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/cut/"
os.makedirs(TMP, exist_ok=True)
src, out, segs, caps = sys.argv[1:5]; ty = int(sys.argv[5]) if len(sys.argv) > 5 else 300
segs = [tuple(map(float, s.split("-"))) for s in segs.split(",")]
dur = sum(b - a for a, b in segs)
LOOK = "eq=contrast=0.98:saturation=0.93:gamma=1.02,noise=alls=6:allf=t,unsharp=3:3:0.2"
fc = [f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[s{i}]" for i, (a, b) in enumerate(segs)]
fc.append("".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,{LOOK}[v0]")
ins = []; cur = "[v0]"
for j, c in enumerate([c for c in caps.split(";") if c]):
    text, t0, t1 = c.split("@"); t1 = dur + 1 if t1 == "end" else float(t1); lines = text.split("|")
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 50)
    while font.size > 34 and max(line_w(l, font) for l in lines) > 1000:
        font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", font.size - 2)
    p = TMP + f"c{j}_{os.path.basename(out)}.png"; render(lines, p, font=font, stroke=3)
    ins += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
    fc.append(f"{cur}[{j+1}:v]overlay=0:{ty}:enable='between(t\\,{float(t0):.3f}\\,{t1:.3f})'[o{j}]"); cur = f"[o{j}]"
fc.append(f"{cur}format=yuv420p[v]")
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src] + ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-an", "-t", f"{dur:.3f}",
    "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M", "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("OK", out, round(dur, 2))
