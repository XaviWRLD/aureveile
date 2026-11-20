"""Reels from the Reels Scout report: G2 gloves 'The problem / The solution' (Mambo No. 5)
and H1 HoHoHound Geschenkpapier-Trend (Sleigh Ride). One line of native text, CTA on screen, beat-cut.
python3 scout_reels.py [G2|H1]"""
import json, subprocess, sys, os, re, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render

U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
C = "/home/user/aureveile/edits/scout_reels/clips/"
OUTD = "/home/user/aureveile/edits/scout_reels/"
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/scout_ov/"
BEATS = json.load(open("/home/user/aureveile/edits/tools/songbeats2.json"))
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
GLOVE_REAL = U + "bed81630-VID-20261112-WA0001.mp4"   # real product footage: button press, 3-bar LED

# segments: (file, src start, out duration or None=until next beat cut, speed)
R = {
 "G2": dict(song="d4eec954-Mambo_No_5.mp3", key="mambo", a0=4.5, hit=6.83, out="Gloves_G2_ProblemSolution_Mambo.mp4",
    pre=(C + "g_problem.mp4", 2.3, 1.0),
    shots=[(GLOVE_REAL, 5.6, 4, 1.0), (C + "g_solution.mp4", 0.4, 8, 1.0), (C + "g_car.mp4", 0.3, 9, 1.0)],
    text=[(["The problem 🥶"], 230, "pre"), (["The solution 🔥"], 230, (0, 3)),
          (["Comment WARM for the link 👇"], 1460, (2, 3))]),
 "H1": dict(song="e73f2714-Sleigh_Ride.mp3", key="sleigh", a0=2.0, hit=4.11, out="HoHoHound_H1_Geschenkpapier_SleighRide.mp4",
    pre=(C + "h_door.mp4", 1.8, 1.0),
    shots=[(C + "h_burst.mp4", 0.0, 3, 1.0), (C + "h_burst.mp4", 0.0, 4, 0.45), (C + "h_family.mp4", 0.3, 5, 1.0)],
    text=[(["Mein Hund macht den", "Geschenkpapier-Trend 🎁"], 230, "all"),
          (["nochmal in Zeitlupe 😂"], 1480, (1, 2)),
          (["Schreib „SANTA“ für den Link 👇"], 1480, (2, 3))]),
}

def build(name, cfg, gain):
    bt = np.array(BEATS[cfg["key"]]["beats"]); i0 = int(np.argmin(abs(bt - cfg["hit"])))
    PRE = bt[i0] - cfg["a0"]; B = lambda k: PRE + float(bt[i0 + k] - bt[i0])
    pf, ps, psp = cfg["pre"]
    ins = [pf] + [s[0] for s in cfg["shots"]]
    fc = [f"[0:v]trim={ps}:{ps + PRE * psp:.3f},setpts=(PTS-STARTPTS)/{psp},fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{PRE:.4f}[p]"]
    cuts = [0.0, PRE]; k = 0; lab = ["[p]"]
    for i, (f, s0, nb, sp) in enumerate(cfg["shots"]):
        d = B(k + nb) - B(k)
        fc.append(f"[{i+1}:v]trim={s0}:{s0 + d * sp:.3f},setpts=(PTS-STARTPTS)/{sp},fps=30,{SC},tpad=stop_mode=clone:stop_duration=2,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        lab.append(f"[c{i}]"); k += nb; cuts.append(B(k))
    total = cuts[-1]
    fc.append("".join(lab) + f"concat=n={len(lab)}:v=1:a=0[cv]")
    zs = "+".join(f"0.06*max(0\\,1-(t-{c:.3f})/0.18)*gte(t\\,{c:.3f})" for c in cuts[1:-1])
    fc.append(f"[cv]scale=w='trunc(1080*(1+{zs})/2)*2':h='trunc(1920*(1+{zs})/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.02:saturation=1.04[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.45*max(0\\,1-(T-{PRE:.3f})/0.14)*gte(T\\,{PRE:.3f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[v0]")
    cur = "[v0]"; extra = []; n = len(ins)
    for j, (lines, y, when) in enumerate(cfg["text"]):
        t0, t1 = (0, PRE) if when == "pre" else (0, total + 1) if when == "all" else (cuts[1 + when[0]] + 0.1, cuts[1 + when[1]] if when[1] < len(cuts) - 1 else total + 1)
        p = render(lines, TMP + f"{name}_{j}.png"); extra += ["-loop", "1", "-i", p]
        fc.append(f"{cur}[{n+j}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1-0.034:.3f})'[o{j}]"); cur = f"[o{j}]"
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    fc.append(f"[{n+len(cfg['text'])}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={total-0.4:.3f}:d=0.4,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    out = OUTD + cfg["out"]
    args = sum([["-i", f] for f in ins], []) + extra + ["-ss", f"{cfg['a0']:.3f}", "-i", U + cfg["song"]]
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "17", "-maxrate", "10M", "-bufsize", "20M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", out], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
    return out, [round(c, 2) for c in cuts]

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    for name in (sys.argv[1:] or R):
        out, cuts = build(name, R[name], 0)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        out, cuts = build(name, R[name], round(-14 - I, 1)); print("OK", name, cuts)
