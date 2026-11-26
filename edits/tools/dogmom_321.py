"""'3-2-1' blanket-reveal Reel (competitor format, German): she says „Drei… zwei… eins!“ while lifting the blanket
a little more each time (nothing shows), then whips it off on the 0:56 drop of 'All I Want for Christmas Is You'.
Organic-looking text: one small native-style line, thin outline, no CTA on screen. Music quiet under the countdown.
python3 dogmom_321.py <clip> <t_drei> <t_zwei> <t_eins> <t_reveal> <out> ["hook"]"""
import re, subprocess, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageFont
from hohohound_9 import render

SONG = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"
VO = os.environ.get("VO", "/home/user/aureveile/edits/hohohound/dogmom/clips/vo_321_helena.wav")
# the 3 spoken words inside the VO file, env WORDS="a-b,c-d,e-f" to override
WORDS = [tuple(float(x) for x in w.split("-")) for w in os.environ.get("WORDS", "0.45-0.98,1.93-2.66,3.50-4.22").split(",")]
DROP = 56.0
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/dm/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
LOOK = ("eq=contrast=0.98:saturation=0.93:gamma=1.02,noise=alls=7:allf=t,unsharp=3:3:0.2" if os.environ.get("REAL") else
        "eq=contrast=1.02:saturation=1.03,unsharp=5:5:0.3")   # REAL=1: phone-like finish (grain, softer colour)
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 46)

def build(src, ts, reveal, out, hook, gain):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout) - 0.05
    lines = hook.split("|"); font = FONT
    from xmas_mums import line_w
    while font.size > 34 and max(line_w(l, font) for l in lines) > 1000:   # never let the hook run off the screen
        font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", font.size - 2)
    png = render(lines, TMP + "hook_org.png", font=font, stroke=3)
    a0 = max(0.0, DROP - reveal)
    fc = [f"[0:v]fps=30,{SC},{LOOK}[v0];[v0][1:v]overlay=0:{int(os.environ.get("TEXT_Y", "300"))}[v1];[v1]trim=0:{dur:.3f},format=yuv420p[v]"]
    # music: quiet under the countdown, full from the drop
    fc.append(f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,volume='if(lt(t\\,{reveal - 0.08:.2f})\\,0.28\\,1)':eval=frame,afade=t=out:st={dur - 0.6:.3f}:d=0.6[m]")
    for k, ((w0, w1), t) in enumerate(zip(WORDS, ts)):
        fc.append(f"[3:a]atrim={w0}:{w1},asetpts=PTS-STARTPTS,volume=1.6,adelay={int(t * 1000)}|{int(t * 1000)}[w{k}]")
    fc.append(f"[m][w0][w1][w2]amix=inputs=4:duration=first:normalize=0,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-i", png, "-ss", f"{a0:.3f}", "-i", SONG, "-i", VO,
        "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur:.3f}", out],
        capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    src = sys.argv[1]; ts = [float(x) for x in sys.argv[2:5]]; reveal = float(sys.argv[5]); out = sys.argv[6]
    hook = sys.argv[7] if len(sys.argv) > 7 else "Zeig das bloß keiner Hundemama… 😍🎄"
    build(src, ts, reveal, out, hook, 0)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    build(src, ts, reveal, out, hook, round(-14 - I, 1)); print("OK", out)
