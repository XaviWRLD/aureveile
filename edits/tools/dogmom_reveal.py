"""German rebuild of the competitor's viral blanket-reveal template (6 US Reels, 30–70K views).
One hook line for the whole video (white, black outline, no CTA on screen), the blanket reveal lands exactly
on the 0:56 drum drop of 'All I Want for Christmas Is You' (same sound and sync as the competitor), slow shots,
no added cuts. -14 LUFS.   python3 dogmom_reveal.py <clip.mp4> <reveal_seconds> <out.mp4> ["hook line 1|line 2"]"""
import re, subprocess, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render

SONG = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"
DROP = 56.0
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/dm/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"

HOLD = float(os.environ.get("HOLD", "0"))   # >0: hold the covered lump this long with a 3-2-1 countdown before the reveal

def build(src, reveal, out, hook, gain):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout) - 0.05 + HOLD
    png = render(hook.split("|"), TMP + "hook.png")
    reveal += HOLD; a0 = max(0.0, DROP - reveal)
    ins = ["-i", src, "-loop", "1", "-i", png, "-ss", f"{a0:.3f}", "-i", SONG]
    if HOLD:   # covered lump: first frame held with a slow push-in, then the clip plays and the blanket is pulled on the drop
        v = (f"[0:v]trim=0:0.04,setpts=PTS-STARTPTS,fps=30,{SC},tpad=stop_mode=clone:stop_duration={HOLD:.3f},trim=0:{HOLD:.3f},"
             f"scale=w='trunc(1080*(1+0.06*t/{HOLD:.2f})/2)*2':h='trunc(1920*(1+0.06*t/{HOLD:.2f})/2)*2':eval=frame,crop=1080:1920,setsar=1[h];"
             f"[0:v]fps=30,{SC}[m];[h][m]concat=n=2:v=1:a=0,")
        nums = []; beeps = []
        for k, n in enumerate(["3", "2", "1"]):
            t0 = HOLD - 3.0 + k + 0.2
            from PIL import Image, ImageDraw
            from hohohound_9 import FB
            im = Image.new("RGBA", (1080, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = d.textlength(n, font=FB)
            d.text(((1080 - w) / 2, 30), n, font=FB, fill="white", stroke_width=9, stroke_fill=(0, 0, 0, 240)); p = TMP + f"n{n}.png"; im.save(p)
            ins += ["-loop", "1", "-i", p]; nums.append((3 + k, t0))
            beeps.append(f"sine=f={660 if k < 2 else 990}:d=0.13,volume=0.35,adelay={int(t0 * 1000)}|{int(t0 * 1000)}[b{k}]")
        fc = v + "eq=contrast=1.03:saturation=1.04,unsharp=5:5:0.35[v0];[v0][1:v]overlay=0:230[vh]"
        cur = "[vh]"
        for j, (idx, t0) in enumerate(nums):
            fc += f";{cur}[{idx}:v]overlay=0:820:enable='between(t\\,{t0:.2f}\\,{t0 + 0.85:.2f})'[c{j}]"; cur = f"[c{j}]"
        fc += f";{cur}trim=0:{dur:.3f},format=yuv420p[v];" + ";".join(beeps) + ";"
        fc += (f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={dur - 0.6:.3f}:d=0.6[m0];"
               f"[m0][b0][b1][b2]amix=inputs=4:duration=first:normalize=0,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    else:
        fc = (f"[0:v]fps=30,{SC},eq=contrast=1.03:saturation=1.04,unsharp=5:5:0.35[v0];[v0][1:v]overlay=0:230[v1];[v1]trim=0:{dur:.3f},format=yuv420p[v];"
              f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={dur - 0.6:.3f}:d=0.6,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "17", "-r", "30", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur:.3f}", out], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    src, reveal, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    hook = sys.argv[4] if len(sys.argv) > 4 else "Zeig das bloß keiner|Hundemama… 😍🎄🐶"
    build(src, reveal, out, hook, 0)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    build(src, reveal, out, hook, round(-14 - I, 1)); print("OK", out)
