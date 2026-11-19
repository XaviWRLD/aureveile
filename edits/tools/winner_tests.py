# Split-test variants of the 470K "Gift warmth" winner. All end on "Comment WARM" + Dec 4 deadline.
import json, subprocess, sys, re, numpy as np
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
SRC = U + "b20696f0-VID-20261112-WA0000.mp4"; SONG = U + "9d88af6e-All_I_Want_for_Christmas_Is_You.mp3"
OUTD = "/home/user/aureveile/edits/winner_tests/"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"
bt = np.array(json.load(open("/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/work/songbeats.json"))["v1_gift"]["beats"])
i0 = int(np.argmin(abs(bt - 49.760))); T = lambda k: float(bt[i0 + k] - bt[i0])
BASE = [(0, .833, 2), (.833, 1.917, 2), (1.917, 2.958, 2), (2.958, 4.083, 2), (4.083, 5.25, 2), (5.25, 6.458, 4),
        (6.458, 8.958, 4), (8.958, 11.042, 4), (11.042, 14.2, 6)]
def esc(s): return s.replace("'", "\u2019").replace(":", "\\:").replace(",", "\\,")
def txt(s, fs, col, y, t0, t1, pop=True, bw=8):
    fs = min(fs, int(1000 / (0.62 * len(s))))
    yy = f"{y}+16*max(0\\,1-(t-{t0:.3f})/0.12)" if pop else str(y)
    return (f"drawtext=fontfile={FONT}:text='{esc(s)}':fontsize={fs}:fontcolor={col}:borderw={bw}:bordercolor=black@0.95:shadowx=0:shadowy=5:"
            f"shadowcolor=black@0.5:x=(w-text_w)/2:y={yy}:alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1-0.06:.3f})'")
def build(name, segs, offset, hook_draw, hook_cover):
    # offset: beats added at start (glow-first). caps defined in beats relative to the BASE timeline.
    fc = []; k = 0; cuts = []
    for i, (a, b, nb) in enumerate(segs):
        d = T(k + nb) - T(k); sp = (b - a) / d; cuts.append(T(k)); k += nb
        fc.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,scale=1080:1890:flags=lanczos,crop=1080:1890,pad=1080:1920:0:15,setsar=1,trim=0:{d:.5f}[s{i}]")
    total = T(k); cuts.append(total)
    fc.append("".join(f"[s{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[cv0]")
    if hook_cover:   # blur the burned-in English hook while it's on screen, then draw the new hook
        c0, c1 = hook_cover
        fc.append(f"[cv0]split[cva][cvb];[cvb]crop=760:330:160:330,boxblur=28:6[blr];[cva][blr]overlay=160:330:enable='between(t\\,{c0:.3f}\\,{c1:.3f})'[cv]")
    else: fc.append("[cv0]null[cv]")
    zs = "+".join(f"0.09*max(0\\,1-(t-{c:.4f})/0.22)*gte(t\\,{c:.4f})" for c in cuts[1:-1])
    sz = f"0.06*between(t\\,{T(offset+22):.3f}\\,{total:.3f})*(t-{T(offset+22):.3f})/{total-T(offset+22):.3f}"
    Z = f"(1+{zs}+{sz})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.06:saturation=1.12[zv]")
    fl = T(offset + 10) if offset == 0 else 0.0
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.75*max(0\\,1-(T-{fl:.4f})/0.18)*gte(T\\,{fl:.4f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
    B = lambda x: T(offset + x)
    dt = [txt(s, fs, c, y, t0, t1, False, 9) for s, fs, c, y, t0, t1 in hook_draw]
    dt += [txt("for the person who’s", 64, "white", 1335, B(4), B(10)), txt("ALWAYS COLD", 82, Y, 1427, B(4), B(10)),
           txt("3 HEAT LEVELS", 82, Y, 1335, B(10), B(14)),
           txt("no more", 64, "white", 1335, B(14), B(22)), txt("FROZEN FINGERS", 82, Y, 1427, B(14), B(22)),
           txt("Comment WARM", 104, Y, 1330, B(22), total + 1), txt("for the link", 76, "white", 1450, B(22), total + 1)]
    fc.append("[fv]" + ",".join(dt) + ",format=yuv420p[v]")
    L = total + 0.6
    def run(gain):
        a = f"[1:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={total:.3f}:d=0.6,volume={gain}dB,alimiter=limit=0.84:level=false[a]"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-ss", f"{bt[i0]-0.015:.3f}", "-i", SONG, "-filter_complex", ";".join(fc + [a]),
            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "18", "-maxrate", "8M", "-bufsize", "16M",
            "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{L:.3f}", OUTD + name], capture_output=True, text=True)
        if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
    run(0)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", OUTD + name, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    run(round(-14 - I, 1)); print(name, f"{L:.2f}s cuts", [round(c, 2) for c in cuts])
import os; os.makedirs(OUTD, exist_ok=True)
# C: original opening + new WARM/deadline ending
build("Winner_C_CommentWARM.mp4", BASE, 0, [], None)
# B: new hook drawn over the blurred burned-in hook (burned hook is on screen through ~2.0s)
hb_end = T(4) + 0.45
build("Winner_B_NewHook.mp4", BASE, 0, [("THE GIFT SHE’LL", 104, "white", 390, 0, hb_end), ("ACTUALLY USE.", 104, Y, 502, 0, hb_end)], (0, hb_end))
# A: glow-first — open on the button lighting up (src 6.95–7.95), our own hook drawn on it, then the original
build("Winner_A_GlowFirst.mp4", [(6.95, 7.95, 2)] + BASE, 2, [("GIFT WARMTH", 110, "white", 330, 0, T(2)), ("THIS WINTER.", 110, Y, 448, 0, T(2))], None)
