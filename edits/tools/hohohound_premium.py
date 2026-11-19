"""Premium single-story HoHoHound Reel from 4K Kling clips with native sound.
Story: store ("Schatz, der Hund braucht das nicht") -> shelf grab -> unbox -> dressing -> trot
-> boyfriend filming & laughing ("Er, 5 Minuten später") -> asleep under the tree (loop)."""
import json, subprocess, sys, re, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render, FT, TMP, U, SONGS, BEATS

P = "/home/user/aureveile/edits/hohohound/premium/"
OUT = P + "HoHoHound_PREMIUM_Schatz.mp4"
song, key, hit = SONGS["mariah"]
bt = np.array(BEATS[key]["beats"]); i0 = int(np.argmin(abs(bt - hit)))
PRE_CLIP, PRE_SS, PRE = "p1_store", 1.0, 3.2
# (clip, src start, beats, ambient volume)
MONT = [("p2_shelf", 0.3, 4, 0.30), ("p3_unbox", 0.0, 6, 0.35), ("p4_dress", 0.6, 7, 0.45),
        ("p5_trot", 0.2, 6, 0.30), ("p6_him", 0.6, 8, 0.55), ("p8_sleep", 0.6, 6, 0.40)]
B = lambda k: PRE + float(bt[i0 + k] - bt[i0])
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"

def build(gain, out):
    ins = [P + PRE_CLIP + ".mp4"] + [P + c + ".mp4" for c, *_ in MONT]
    fc = [f"[0:v]trim={PRE_SS}:{PRE_SS + PRE:.3f},setpts=PTS-STARTPTS,{SC},fps=30[p]",
          f"[0:a]atrim={PRE_SS}:{PRE_SS + PRE:.3f},asetpts=PTS-STARTPTS,volume=0.85[ap]"]
    cuts = [0.0, PRE]; k = 0; vl = ["[p]"]; al = ["[ap]"]
    for i, (c, s0, nb, av) in enumerate(MONT):
        d = B(k + nb) - B(k)
        fc.append(f"[{i+1}:v]trim={s0}:{s0 + d:.4f},setpts=PTS-STARTPTS,{SC},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        fc.append(f"[{i+1}:a]atrim={s0}:{s0 + d:.4f},asetpts=PTS-STARTPTS,apad,atrim=0:{d:.4f},afade=t=in:d=0.03,afade=t=out:st={d-0.04:.4f}:d=0.04,volume={av}[a{i}]")
        vl.append(f"[c{i}]"); al.append(f"[a{i}]"); k += nb; cuts.append(B(k))
    total = cuts[-1]
    fc.append("".join(vl) + f"concat=n={len(vl)}:v=1:a=0[cv]")
    fc.append("".join(al) + f"concat=n={len(al)}:v=0:a=1,highpass=f=80[amb]")
    zs = "+".join(f"0.05*max(0\\,1-(t-{c:.3f})/0.18)*gte(t\\,{c:.3f})" for c in cuts[1:-1])
    Z = f"(1+0.03*max(0\\,1-t/0.3)+{zs})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.02:saturation=1.04,unsharp=5:5:0.35[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.4*max(0\\,1-(T-{PRE:.3f})/0.14)*gte(T\\,{PRE:.3f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[v0]")
    him0, him1 = cuts[5], cuts[6]
    ov = [(render(["„Schatz, der Hund braucht", "das nicht.“ 🙄"], TMP + "pr_hook.png"), 230, 0, him0),
          (render(["Ich: 😍🎄"], TMP + "pr_ich.png", align="left"), 940, 1.3, him0),
          (render(["Er, 5 Minuten später: 🥲"], TMP + "pr_him.png"), 230, him0, him1),
          (render(["„Schatz, der Hund braucht", "das nicht.“ 🙄"], TMP + "pr_hook2.png"), 230, him1, total + 1),
          (render(["Schreib „SANTA“ für den Link 👇"], TMP + "pr_cta.png"), 1540, him1 + 0.2, total + 1)]
    cur = "[v0]"; extra = []; n = len(ins)
    for j, (png, y, t0, t1) in enumerate(ov):
        extra += ["-loop", "1", "-i", png]
        fc.append(f"{cur}[{n+j}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1-0.034:.3f})':eof_action=pass[o{j}]")
        cur = f"[o{j}]"
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    m = n + len(ov)
    fc.append(f"[{m}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={total-0.45:.3f}:d=0.45[mus]")
    # music ducks a little under the store squeal and his laugh
    fc.append(f"[mus]volume='1-0.35*between(t\\,0\\,{PRE:.3f})-0.25*between(t\\,{him0:.3f}\\,{him1:.3f})':eval=frame[mus2]")
    fc.append(f"[mus2][amb]amix=inputs=2:duration=first:normalize=0,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    args = sum([["-i", f] for f in ins], []) + extra + ["-ss", f"{bt[i0] - PRE - 0.015:.3f}", "-i", U + song]
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "15", "-maxrate", "12M", "-bufsize", "24M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{total:.3f}", out],
        capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2500:]); sys.exit(1)
    return cuts

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    build(0, OUT)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", OUT, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    print("OK", [round(c, 2) for c in build(round(-14 - I, 1), OUT)])
