"""HoHoHound German Reel: store hook -> unboxing (drop) -> dog trot -> asleep loop.
Usage: python3 hohohound_de.py  (clips c1..c4.mp4 + emoji.png in SRC)"""
import json, subprocess, sys, re, numpy as np
SRC = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/hh/"
SONG = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"
OUT = "/home/user/aureveile/edits/hohohound/HoHoHound_DE_Schatz.mp4"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"
bt = np.array(json.load(open("/home/user/aureveile/edits/tools/songbeats.json"))["v1_gift"]["beats"])
HIT = 49.760; i0 = int(np.argmin(abs(bt - HIT)))
PRE_SRC = (0.6, 4.2)                      # store clip before the drop (output 3.6 s at 1.0x)
PRE = PRE_SRC[1] - PRE_SRC[0]
T = lambda k: PRE + float(bt[i0 + k] - bt[i0])
POST = [(1, 0.2, 3.1, 7), (2, 0.0, 4.6, 11), (3, 0.0, 4.4, 9)]   # (input, src a, src b, beats)

def esc(s): return s.replace("'", "\u2019").replace(":", "\\:").replace(",", "\\,")
def txt(s, fs, col, y, t0, t1, pop=True, x="(w-text_w)/2"):
    fs = min(fs, int(1000 / (0.6 * len(s))))
    yy = f"{y}+16*max(0\\,1-(t-{t0:.3f})/0.12)" if pop else str(y)
    return (f"drawtext=fontfile={FONT}:text='{esc(s)}':fontsize={fs}:fontcolor={col}:borderw=9:bordercolor=black@0.95:shadowx=0:shadowy=5:"
            f"shadowcolor=black@0.5:x={x}:y={yy}:alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1-0.07:.3f})'")
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"

def build(gain):
    fc = [f"[0:v]trim={PRE_SRC[0]}:{PRE_SRC[1]},setpts=PTS-STARTPTS,fps=30,{SC}[p]"]
    k = 0; cuts = [0.0, PRE]; labels = ["[p]"]
    for i, (inp, a, b, nb) in enumerate(POST):
        d = T(k + nb) - T(k); sp = (b - a) / d
        fc.append(f"[{inp}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        labels.append(f"[c{i}]"); k += nb; cuts.append(T(k))
    total = cuts[-1]
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cv]")
    zs = "+".join(f"0.07*max(0\\,1-(t-{c:.3f})/0.2)*gte(t\\,{c:.3f})" for c in cuts[1:-1])
    Z = f"(1+0.04*max(0\\,1-t/0.35)+{zs})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.03:saturation=1.06[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.55*max(0\\,1-(T-{PRE:.3f})/0.16)*gte(T\\,{PRE:.3f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
    c = cuts
    ich_t = 1.3                                  # "Ich: 😍" lands after the line is read
    dt = [txt("„Schatz, der Hund", 84, "white", 230, 0, PRE, False), txt("braucht das nicht.“", 84, "white", 330, 0, PRE, False),
          txt("Ich:", 104, Y, 455, ich_t, PRE, True, "(w-text_w)/2-70"),
          txt("Er braucht es.", 96, Y, 1380, c[1], c[2]),
          txt("Der Weihnachtsmann", 78, "white", 250, c[2], c[3]), txt("REITET MIT", 104, Y, 345, c[2], c[3]),
          txt("Schreib SANTA", 100, Y, 1330, c[3], total + 1), txt("für den Link", 76, "white", 1450, c[3], total + 1)]
    fc.append("[fv]" + ",".join(dt) + "[tv]")
    fc.append(f"[tv][4:v]overlay=x=W/2+40:y=455+2+12*max(0\\,1-(t-{ich_t})/0.12):enable='between(t\\,{ich_t}\\,{PRE-0.07:.3f})',format=yuv420p[v]")
    L = total + 0.4
    fc.append(f"[5:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={total-0.3:.3f}:d=0.7,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    ins = [SRC + f"c{i}.mp4" for i in range(1, 5)]
    args = sum([["-i", f] for f in ins], []) + ["-loop", "1", "-i", SRC + "emoji.png", "-ss", f"{bt[i0]-PRE-0.015:.3f}", "-i", SONG]
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args +
        ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "18",
         "-maxrate", "8M", "-bufsize", "16M", "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{L:.3f}", OUT],
        capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
    return cuts

if __name__ == "__main__":
    import os; os.makedirs(os.path.dirname(OUT), exist_ok=True)
    build(0)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", OUT, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    print("OK", [round(x, 2) for x in build(round(-14 - I, 1))])
