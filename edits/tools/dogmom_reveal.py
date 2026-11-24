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

def build(src, reveal, out, hook, gain):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout) - 0.05
    png = render(hook.split("|"), TMP + "hook.png")
    a0 = max(0.0, DROP - reveal)
    fc = (f"[0:v]fps=30,{SC},eq=contrast=1.03:saturation=1.04,unsharp=5:5:0.35[v0];[v0][1:v]overlay=0:230[v1];[v1]trim=0:{dur:.3f},format=yuv420p[v];"
          f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={dur - 0.6:.3f}:d=0.6,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-i", png, "-ss", f"{a0:.3f}", "-i", SONG, "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "17", "-r", "30", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur:.3f}", out], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    src, reveal, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    hook = sys.argv[4] if len(sys.argv) > 4 else "Zeig das bloß keiner|Hundemama… 😍🎄🐶"
    build(src, reveal, out, hook, 0)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    build(src, reveal, out, hook, round(-14 - I, 1)); print("OK", out)
