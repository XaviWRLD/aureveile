# Variations of the supermarket-reveal edit: same 3-2-1 reveal, different song / unboxing / b-roll / captions.
import json, subprocess, sys, re, numpy as np
VAR = sys.argv[1]
SP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/"
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
INPUTS = [U + "59599c1b-hf_20261117_200618_a3125ef2-897a-42f7-a124-9fb3a2aebd1a.mp4",   # 0 genjutsu reveal
          U + "3727053c-VID-20261112-WA0002.mp4",                                       # 1 v3 source
          U + "bed81630-VID-20261112-WA0001.mp4",                                       # 2 v2 source
          None,                                                                         # 3 song (set per variant)
          SP + "sep/countdown_vocals.flac",                                             # 4 isolated countdown
          SP + "hf/gen/unbox.mp4",                                                      # 5 living-room unboxing
          SP + "hf/gen/unbox_kitchen.mp4",                                              # 6 kitchen unboxing
          U + "b20696f0-VID-20261112-WA0000.mp4"]                                       # 7 v1 source
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"
CFG = {
 "V2_Housewife": dict(song="27fc37e0-Housewife.mp3", key="v2_coldhands", hit=37.198,
   hook=[("HUSBANDS, TAKE NOTES.", 74, "white", 150), ("SHE WANTS THESE.", 96, Y, 250)], cd_y=560,
   clips=[(6, 1.0, 5.0, 9), (2, 5.417, 6.833, 3), (2, 11.25, 12.458, 3), (2, 12.458, 14.042, 4), (1, 13.458, 15.1, 5)],
   caps=[[("IT’S HERE.", 100, Y, 1380)], [("ONE CLICK.", 100, Y, 1380)], [("out the door", 84, "white", 1380)],
         [("warm hands", 76, "white", 1330), ("ALL WINTER", 100, Y, 1425)],
         [("Comment WARM", 104, Y, 1330), ("for the link", 76, "white", 1450)]]),
 "V3_LastChristmas": dict(song="09c4c148-Last_Christmas.mp3", key="v3_heatup", hit=7.709,
   hook=[("UNPOPULAR OPINION", 74, "white", 140), ("NORMAL GLOVES", 100, Y, 230), ("ARE USELESS.", 100, Y, 340)], cd_y=660,
   clips=[(5, 1.0, 4.98, 7), (7, 6.85, 7.95, 2), (1, 11.667, 13.458, 3), (7, 11.042, 14.2, 5)],
   caps=[[("BEST GIFT THIS YEAR.", 88, Y, 1380)], [("ONE CLICK.", 100, Y, 1380)],
         [("warm hands", 76, "white", 1330), ("ALL WINTER", 100, Y, 1425)],
         [("Comment WARM", 104, Y, 1330), ("for the link", 76, "white", 1450)]]),
}[VAR]
INPUTS[3] = U + CFG["song"]
import os
INPUTS = [f if (f is None or os.path.exists(f)) else INPUTS[5] for f in INPUTS]
OUT = f"/home/user/aureveile/edits/genjutsu/HeatedGloves_Reveal_{VAR}.mp4"
bt = np.array(json.load(open(SP + "work/songbeats.json"))[CFG["key"]]["beats"])
HIT_OUT = 4.35; ih = int(np.argmin(abs(bt - CFG["hit"])))
T = lambda k: float(bt[ih + k] - bt[ih]) + HIT_OUT
SS = CFG["hit"] - HIT_OUT; REV_END_K = 2
def build(gain):
    fc = []; rev_len = T(REV_END_K)
    fc.append(f"[0:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=1,trim=0:{rev_len:.4f},setpts=PTS-STARTPTS[r]")
    k = REV_END_K; cuts = [rev_len]; labels = ["[r]"]
    for i, (inp, a, b, nb) in enumerate(CFG["clips"]):
        d = T(k + nb) - T(k); sp = min((b - a) / d, 3)
        fc.append(f"[{inp}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,"
                  f"tpad=stop_mode=clone:stop_duration=2,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        labels.append(f"[c{i}]"); k += nb; cuts.append(T(k))
    total = cuts[-1]
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cv]")
    zs = "+".join(f"0.08*max(0\\,1-(t-{c:.3f})/0.2)*gte(t\\,{c:.3f})" for c in cuts[:-1])
    fc.append(f"[cv]scale=w='trunc(1080*(1+{zs})/2)*2':h='trunc(1920*(1+{zs})/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.7*max(0\\,1-(T-{HIT_OUT})/0.15)*gte(T\\,{HIT_OUT})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
    def txt(s, fs, col, y, t0, t1, pop=True):
        yy = f"{y}+16*max(0\\,1-(t-{t0:.3f})/0.12)" if pop else str(y)
        return (f"drawtext=fontfile={FONT}:text='{s}':fontsize={fs}:fontcolor={col}:borderw=8:bordercolor=black@0.95:shadowx=0:shadowy=5:"
                f"shadowcolor=black@0.5:x=(w-text_w)/2:y={yy}:alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1-0.08:.3f})'")
    dt = [txt(h, min(fs, int(1000 / (0.62 * len(h)))), col, y, 0, HIT_OUT, False) for h, fs, col, y in CFG["hook"]]
    for n, t0 in (("3", 0.40), ("2", 1.50), ("1", 2.60)):
        t1 = t0 + 0.9
        dt.append(f"drawtext=fontfile={FONT}:text='{n}':fontsize='300+140*max(0\\,1-(t-{t0})/0.18)':fontcolor=white:borderw=12:bordercolor=black@0.9:"
                  f"x=(w-text_w)/2:y={CFG['cd_y']}-text_h/2:alpha='min(1\\,(t-{t0})/0.06)*min(1\\,({t1}-t)/0.15)':enable='between(t\\,{t0}\\,{t1})'")
    for i, lines in enumerate(CFG["caps"]):
        t1 = cuts[i + 1] if i + 1 < len(cuts) - 1 else total + 1
        for s, fs, col, y in lines: dt.append(txt(s, fs, col, y, cuts[i], t1))
    fc.append("[fv]" + ",".join(dt) + ",format=yuv420p[v]")
    L = total
    fc.append(f"[3:a]atrim=0:{L+0.3:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={L-0.6:.3f}:d=0.9[mus];"
              f"[4:a]atrim=0:{HIT_OUT:.3f},asetpts=PTS-STARTPTS,highpass=f=90,volume=0.8,afade=t=out:st={HIT_OUT-0.3:.3f}:d=0.3,apad[cnt];"
              f"[mus][cnt]amix=inputs=2:duration=first:normalize=0,volume={gain}dB,alimiter=limit=0.84:attack=2:release=60:level=false[a]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for j, f in enumerate(INPUTS):
        if j == 3: cmd += ["-ss", f"{SS:.3f}"]
        cmd += ["-i", f]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-r", "30",
            "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", "-t", f"{L+0.3:.3f}", OUT]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
    return cuts
build(0)
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", OUT, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
cuts = build(round(-14 - I, 1))
print(VAR, "OK", f"total={cuts[-1]:.2f}s cuts={[round(x,2) for x in cuts]}")
