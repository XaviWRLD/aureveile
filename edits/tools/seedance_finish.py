"""Finish a multi-shot Seedance clip into a Reel: detect its hard cuts, start the song so its hit lands on
the first cut, zoom-punch each cut, add native text (hook until cut 1, CTA on the last shot), -14 LUFS.
python3 seedance_finish.py G1|H2"""
import json, subprocess, sys, os, re, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render

U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
D = "/home/user/aureveile/edits/scout_reels/"
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/scout_ov/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
J = {
 "G1": dict(src=D + "clips/g1_seedance.mp4", song=U + "d078ba83-Be_My_Baby.mp3", hit=4.2, out=D + "Gloves_G1_DoNotShow_BeMyBaby.mp4",
    hook=["DO NOT show this to a girl", "who gets cold easily… 🥶"], me=(["Me:"], 1), cta=["Comment WARM for the link 👇"]),
 "H2": dict(src=D + "clips/h2_seedance.mp4", song=U + "b488bde6-All_I_Want_for_Christmas_Is_You.mp3", hit=49.76, out=D + "HoHoHound_H2_Quatsch_Weihnachtsmarkt.mp4",
    hook=["„Hör auf, so einen Quatsch", "für den Hund zu kaufen…“"], me=(["Ich:"], 1), cta=["Schreib „SANTA“ für den Link 👇"]),
    "H3": dict(src=D + "clips/h3_seedance.mp4", song=U + "d4eec954-Mambo_No_5.mp3", hit=6.83, out=D + "HoHoHound_H3_KeineHundemama_Parade.mp4",
    hook=["Lass das KEINE", "Hundemama sehen… 🐶😂"], me=(["Ich, eine Woche später:"], 1), cta=["Schreib „SANTA“ für den Link 👇"]),
 "H4": dict(src=D + "clips/h4_seedance.mp4", song=U + "115c4178-Christmas_Baby_Please_Come_Home.mp3", hit=12.12, out=D + "HoHoHound_H4_Opa_Geschenk.mp4",
    hook=["Das perfekte Weihnachtsgeschenk", "für Opas Hund gibt es nicht…"], me=(["…doch, gibt es 🥹"], 1), cta=["Schreib „SANTA“ für den Link 👇"]),
}

def cuts_of(f):
    e = subprocess.run(["ffmpeg", "-i", f, "-vf", "select='gt(scene,0.28)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    ts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", e)]
    out = []
    for t in ts:
        if t > 0.8 and (not out or t - out[-1] > 1.0): out.append(t)
    return out

def build(name, gain):
    c = J[name]; dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c["src"]], capture_output=True, text=True).stdout)
    cuts = cuts_of(c["src"]); c1 = cuts[0] if cuts else 3.0
    a0 = max(0.0, c["hit"] - c1)
    total = dur - 0.05
    zs = "+".join(f"0.06*max(0\\,1-(t-{x:.3f})/0.18)*gte(t\\,{x:.3f})" for x in cuts) or "0"
    fc = [f"[0:v]fps=30,{SC},scale=w='trunc(1080*(1+{zs})/2)*2':h='trunc(1920*(1+{zs})/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.03:saturation=1.04,unsharp=5:5:0.4[v0]"]
    last = cuts[-1] if len(cuts) > 1 else total - 3
    ov = [(render(c["hook"], TMP + f"{name}_h.png"), 230, 0, c1),
          (render(c["me"][0], TMP + f"{name}_me.png"), 230, c1, last),
          (render(c["cta"], TMP + f"{name}_c.png"), 1460, last + 0.1, total + 1)]
    cur = "[v0]"; extra = []
    for j, (p, y, t0, t1) in enumerate(ov):
        extra += ["-loop", "1", "-i", p]
        fc.append(f"{cur}[{1+j}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1-0.034:.3f})'[o{j}]"); cur = f"[o{j}]"
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    fc.append(f"[{1+len(ov)}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={total-0.4:.3f}:d=0.4,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c["src"]] + extra + ["-ss", f"{a0:.3f}", "-i", c["song"], "-filter_complex", ";".join(fc),
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "17", "-maxrate", "10M", "-bufsize", "20M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", c["out"]], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
    return cuts, a0

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    for n in sys.argv[1:] or J:
        build(n, 0); o = J[n]["out"]
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", o, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        print("OK", n, build(n, round(-14 - I, 1)))
