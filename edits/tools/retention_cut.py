import json, subprocess, sys, re, os, numpy as np
G = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/hf/gen/"
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
INP = [G + "scene1.mp4", U + "b20696f0-VID-20261112-WA0000.mp4", G + "scene2.mp4", G + "scene3.mp4", U + "9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"]
OUT = "/home/user/aureveile/edits/winner_tests/Winner_D_NewScenes.mp4"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"
bt = np.array(json.load(open("/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/work/songbeats.json"))["v1_gift"]["beats"])
HIT = 49.760; i0 = int(np.argmin(abs(bt - HIT)))
PRE_SRC = (0.0, 3.0); PRE_SP = 1.1; PRE = (PRE_SRC[1] - PRE_SRC[0]) / PRE_SP   # output time of the hit
T = lambda k: PRE + float(bt[i0 + k] - bt[i0])
POST = [(0, 3.0, 4.8, 4), (1, 6.85, 7.95, 3), (2, 0.4, 5.0, 10), (3, 0.0, 4.0, 10)]
def esc(s): return s.replace("'", "\u2019").replace(":", "\\:").replace(",", "\\,")
def txt(s, fs, col, y, t0, t1, pop=True):
    fs = min(fs, int(1000 / (0.62 * len(s))))
    yy = f"{y}+16*max(0\\,1-(t-{t0:.3f})/0.12)" if pop else str(y)
    return (f"drawtext=fontfile={FONT}:text='{esc(s)}':fontsize={fs}:fontcolor={col}:borderw=9:bordercolor=black@0.95:shadowx=0:shadowy=5:"
            f"shadowcolor=black@0.5:x=(w-text_w)/2:y={yy}:alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1-0.06:.3f})'")
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
def build(gain):
    fc = [f"[0:v]trim={PRE_SRC[0]}:{PRE_SRC[1]},setpts=(PTS-STARTPTS)/{PRE_SP},fps=30,{SC},trim=0:{PRE:.4f}[p]"]
    k = 0; cuts = [0.0, PRE]; labels = ["[p]"]
    for i, (inp, a, b, nb) in enumerate(POST):
        d = T(k + nb) - T(k); sp = (b - a) / d
        fc.append(f"[{inp}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        labels.append(f"[c{i}]"); k += nb; cuts.append(T(k))
    total = cuts[-1]
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cv]")
    zs = "+".join(f"0.08*max(0\\,1-(t-{c:.3f})/0.2)*gte(t\\,{c:.3f})" for c in cuts[1:-1])
    Z = f"(1+0.05*max(0\\,1-t/0.35)+{zs})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.04:saturation=1.08[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.6*max(0\\,1-(T-{PRE:.3f})/0.16)*gte(T\\,{PRE:.3f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
    c = cuts  # c[1]=hit/relief, c[2]=one click, c[3]=gift, c[4]=night walk, c[5]=end
    walk_cta = c[4] + (c[5] - c[4]) * 0.4
    dt = [txt("ALWAYS-COLD HANDS?", 78, "white", 255, 0, PRE, False), txt("WATCH HER FACE.", 104, Y, 360, 0, PRE, False),
          txt("ONE CLICK.", 104, Y, 1380, c[2], c[3]),
          txt("THE GIFT SHE’LL", 92, "white", 250, c[3], c[4]), txt("ACTUALLY USE.", 104, Y, 360, c[3], c[4]),
          txt("warm hands", 76, "white", 1330, c[4], walk_cta), txt("ALL WINTER", 100, Y, 1425, c[4], walk_cta),
          txt("Comment WARM", 108, Y, 1330, walk_cta, total + 1), txt("for the link", 78, "white", 1452, walk_cta, total + 1)]
    fc.append("[fv]" + ",".join(dt) + ",format=yuv420p[v]")
    L = total + 0.5
    fc.append(f"[4:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={total-0.3:.3f}:d=0.8,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + sum([["-ss", f"{bt[i0]-PRE-0.015:.3f}", "-i", f] if j == 4 else ["-i", f] for j, f in enumerate(INP)], []) +
        ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "18",
         "-maxrate", "8M", "-bufsize", "16M", "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{L:.3f}", OUT],
        capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
    return cuts
build(0)
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", OUT, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
cuts = build(round(-14 - I, 1)); print("OK", [round(x, 2) for x in cuts])
