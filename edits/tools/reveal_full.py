import json, subprocess, numpy as np
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
GEN = U + "59599c1b-hf_20261117_200618_a3125ef2-897a-42f7-a124-9fb3a2aebd1a.mp4"
V3 = U + "3727053c-VID-20261112-WA0002.mp4"; V2 = U + "bed81630-VID-20261112-WA0001.mp4"
SONG = U + "9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"
OUT = "/home/user/aureveile/edits/genjutsu/HeatedGloves_Reveal_FULL.mp4"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"
bt = np.array(json.load(open("/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/work/songbeats.json"))["v1_gift"]["beats"])
HIT_SONG, HIT_OUT = 49.760, 4.35
ih = int(np.argmin(abs(bt - HIT_SONG)))
T = lambda k: float(bt[ih + k] - bt[ih]) + HIT_OUT          # output time of k-th beat after the hit
SS = HIT_SONG - HIT_OUT
# clips after the reveal: (input, src_in, src_out, beats)
clips = [(1, 2.875, 3.958, 4), (1, 13.458, 15.1, 4), (2, 12.458, 14.042, 4), (2, 14.042, 15.12, 6)]
REV_END_K = 2
fc = []
# reveal segment: genjutsu 0 -> T(2) (hold last frame)
rev_len = T(REV_END_K)
fc.append(f"[0:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=1,trim=0:{rev_len:.4f},setpts=PTS-STARTPTS[r]")
k = REV_END_K; cuts = [rev_len]; labels = ["[r]"]
for i, (inp, a, b, nb) in enumerate(clips):
    d = T(k + nb) - T(k); sp = min((b - a) / d, 3)
    fc.append(f"[{inp}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,scale=1097:1920:flags=lanczos,crop=1080:1920,setsar=1,"
              f"tpad=stop_mode=clone:stop_duration=2,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
    labels.append(f"[c{i}]"); k += nb; cuts.append(T(k))
total = cuts[-1]
fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cv]")
zs = "+".join(f"0.08*max(0\\,1-(t-{c:.3f})/0.2)*gte(t\\,{c:.3f})" for c in cuts[:-1])
Z = f"(1+{zs})"
fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2[zv]")
fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.7*max(0\\,1-(T-{HIT_OUT})/0.15)*gte(T\\,{HIT_OUT})'[fl]")
fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
def txt(s, fs, col, y, t0, t1, pop=True):
    yy = f"{y}+16*max(0\\,1-(t-{t0:.3f})/0.12)" if pop else str(y)
    return (f"drawtext=fontfile={FONT}:text='{s}':fontsize={fs}:fontcolor={col}:borderw=8:bordercolor=black@0.95:shadowx=0:shadowy=5:"
            f"shadowcolor=black@0.5:x=(w-text_w)/2:y={yy}:alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1:.3f})'")
dt = [txt("ALWAYS-COLD PEOPLE", 78, "white", 150, 0, HIT_OUT, False), txt("DON’T WALK. THEY RUN.", 78, Y, 245, 0, HIT_OUT, False)]
for n, t0 in (("3", 0.40), ("2", 1.50), ("1", 2.60)):
    t1 = t0 + 0.9
    dt.append(f"drawtext=fontfile={FONT}:text='{n}':fontsize='300+140*max(0\\,1-(t-{t0})/0.18)':fontcolor=white:borderw=12:bordercolor=black@0.9:"
              f"x=(w-text_w)/2:y=560-text_h/2:alpha='min(1\\,(t-{t0})/0.06)*min(1\\,({t1}-t)/0.15)':enable='between(t\\,{t0}\\,{t1})'")
c = cuts
dt += [txt("ONE CLICK.", 96, Y, 1380, c[0], c[1]), txt("3 HEAT LEVELS", 96, Y, 1380, c[1], c[2]),
       txt("warm hands", 76, "white", 1330, c[2], c[3]), txt("ALL WINTER", 100, Y, 1425, c[2], c[3]),
       txt("Comment WARM", 104, Y, 1330, c[3], total + 1), txt("for the link", 76, "white", 1450, c[3], total + 1)]
fc.append("[fv]" + ",".join(dt) + ",format=yuv420p[v]")
L = total
fc.append(f"[3:a]atrim=0:{L+0.3:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={L-0.6:.3f}:d=0.9,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.80:level=false[a]")
cmd = ["ffmpeg", "-v", "error", "-y", "-i", GEN, "-i", V3, "-i", V2, "-ss", f"{SS:.3f}", "-i", SONG, "-filter_complex", ";".join(fc),
       "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-r", "30", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "256k", "-t", f"{L+0.3:.3f}", OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print("OK" if r.returncode == 0 else r.stderr[-1500:], f"total={L:.2f}s cuts={[round(x,2) for x in c]}")
