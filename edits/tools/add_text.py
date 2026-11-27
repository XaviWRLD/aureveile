"""Add timed text overlays to a finished Reel (audio copied).
python3 add_text.py <in.mp4> <out.mp4> "<line1|line2>@<y>@<t0>@<t1>@<style>" ...
style: s = white with outline (native), b = black text on white box (CTA). t1 = end for 'to the end'."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageFont
from hohohound_9 import render
from xmas_mums import render_box, line_w

TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/at/"

def main(src, out, specs):
    os.makedirs(TMP, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    ins, fc, cur = [], [], "[0:v]"
    for j, spec in enumerate(specs):
        text, y, t0, t1, style = spec.split("@")
        lines = text.split("|"); t1 = dur + 1 if t1 == "end" else float(t1); t0 = float(t0); p = TMP + f"t{j}.png"
        if style == "b":
            render_box(lines, p)
        else:
            font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 50)
            while font.size > 34 and max(line_w(l, font) for l in lines) > 1000:
                font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", font.size - 2)
            render(lines, p, font=font, stroke=3)
        ins += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
        fc.append(f"{cur}[{j+1}:v]overlay=0:{int(y)}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1:.3f})'[o{j}]"); cur = f"[o{j}]"
    fc.append(f"{cur}format=yuv420p[v]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src] + ins + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "0:a?",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "copy", out], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
    print("OK", out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
