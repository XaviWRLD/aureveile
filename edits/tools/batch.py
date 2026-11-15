# Batch: retime 42 videos so each song's hit lands on the reveal cut; post-reveal cuts snap to real beats.
import subprocess, json, sys, os, re, numpy as np
from concurrent.futures import ThreadPoolExecutor
W = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(W, "..", "src"); OUT = sys.argv[1]
SONGDIR = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
R = json.load(open(os.path.join(W, "songbeats.json")))
SONGS = {"mariah": (R["v1_gift"], 49.760, "AIWFCIY"), "housewife": (R["v2_coldhands"], 37.198, "Housewife"),
         "lastxmas": (R["v3_heatup"], 7.709, "LastChristmas")}
EN = {**{n: "mariah" for n in (3, 5, 6, 7, 8, 15, 20)}, **{n: "housewife" for n in (1, 2, 4, 10, 11, 12, 21)},
      **{n: "lastxmas" for n in (9, 13, 14, 16, 17, 18, 19)}}
DE = dict(EN); DE.update({2: "lastxmas", 10: "lastxmas", 12: "lastxmas"})
def cuts_of(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-vf", "select='gt(scene,0.3)',showinfo", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"pts_time:([0-9.]+)", out)]
def dur_of(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
def render(job):
    lang, n = job; song = (EN if lang == "En" else DE)[n]
    src = f"{SRC}/{lang}{n:02d}.mp4"; D = dur_of(src) - 0.05
    c = [x for x in cuts_of(src) if 1.0 < x < D - 0.3]
    bnds = [0.0] + c + [D]
    segs = [(a, b) for a, b in zip(bnds, bnds[1:])]
    merged = []  # merge slivers
    for a, b in segs:
        if merged and b - a < 0.35: merged[-1] = (merged[-1][0], b)
        else: merged.append((a, b))
    meta, hit, tag = SONGS[song]; bt = np.array(meta["beats"]); ih = int(np.argmin(abs(bt - hit)))
    hook = merged[0]; hd = hook[1] - hook[0]
    plan = [(hook[0], hook[1], hd)]  # hook at natural speed; music starts hd before the hit
    k = ih; outcuts = [hd]
    for a, b in merged[1:]:
        d = b - a; ibi = bt[k + 1] - bt[k]
        nb = max(1, int(round(d / ibi)))
        while nb > 1 and d / (bt[k + nb] - bt[k]) < 0.85: nb -= 1
        while d / (bt[k + nb] - bt[k]) > 1.25: nb += 1
        od = bt[k + nb] - bt[k]; plan.append((a, b, od)); k += nb; outcuts.append(outcuts[-1] + od)
    total = outcuts[-1]
    fc = []
    for i, (a, b, od) in enumerate(plan):
        sp = (b - a) / od
        fc.append(f"[0:v]trim={a:.4f}:{b:.4f},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,setsar=1,trim=0:{od:.5f}[s{i}]")
    fc.append("".join(f"[s{i}]" for i in range(len(plan))) + f"concat=n={len(plan)}:v=1:a=0[cv]")
    zs = "+".join(f"0.07*max(0\\,1-(t-{t:.4f})/0.2)*gte(t\\,{t:.4f})" for t in outcuts[:-1])
    Z = f"(1+{zs})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,"
              f"crop=1080:1920:(iw-1080)/2:(ih-1920)/2[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,"
              f"geq=r=255:g=255:b=255:a='255*0.7*max(0\\,1-(T-{hd:.4f})/0.16)*gte(T\\,{hd:.4f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1,format=yuv420p[v]")
    ss = bt[ih] - hd - 0.015; L = total + 0.5
    fc.append(f"[1:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={total-0.25:.3f}:d=0.75,"
              f"loudnorm=I=-14:TP=-1.0[aout]")
    name = f"{lang}{n:02d}_{tag}.mp4"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ss", f"{ss:.3f}", "-i", SONGDIR + meta_file(song),
        "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-profile:v", "high", "-r", "30", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k",
        "-ar", "44100", "-t", f"{L:.3f}", f"{OUT}/{lang}/{name}"], capture_output=True, text=True)
    return f"{name} hook={hd:.2f}s total={L:.2f}s segs={len(plan)} {'OK' if r.returncode == 0 else 'FAIL ' + r.stderr[-300:]}"
def meta_file(song): return {"mariah": R["v1_gift"]["file"], "housewife": R["v2_coldhands"]["file"], "lastxmas": R["v3_heatup"]["file"]}[song]
os.makedirs(f"{OUT}/En", exist_ok=True); os.makedirs(f"{OUT}/De", exist_ok=True)
jobs = [(l, n) for n in range(1, 22) for l in ("En", "De")]
if len(sys.argv) > 2: jobs = [(sys.argv[2][:2], int(sys.argv[2][2:]))]
with ThreadPoolExecutor(4) as ex:
    for line in ex.map(render, jobs): print(line, flush=True)
