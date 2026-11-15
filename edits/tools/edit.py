import subprocess, sys, os
UP = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
W = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YEL = "0xFFC23A"
# segments: (src_in, src_out, beats). Speed = src_dur / (beats*beat).
VIDS = {
 "v1_gift": dict(src=UP+"b20696f0-VID-20261112-WA0000.mp4", bpm=150, beat="beats/beat_v1_gift_150bpm.wav",
   song="All I Want for Christmas Is You - Mariah Carey (150 BPM)",
   segs=[(0,.833,2),(.833,1.917,2),(1.917,2.958,2),(2.958,4.083,2),(4.083,5.25,2),(5.25,6.458,4),
         (6.458,8.958,4),(8.958,11.042,4),(11.042,14.2,6)],
   flash=[10], slowzoom=[(22,28)],
   caps=[(4,10,"for the person who's",None),(4,10,"ALWAYS COLD",YEL),
         (10,14,"3 HEAT LEVELS",YEL),
         (14,22,"no more",None),(14,22,"FROZEN FINGERS",YEL),
         (22,28,"gift = sorted",None),(22,28,"LINK IN BIO",YEL)]),
 "v2_coldhands": dict(src=UP+"bed81630-VID-20261112-WA0001.mp4", bpm=133, beat="beats/beat_v2_pov_133bpm.wav",
   song="Housewife - Tate McRae (133 BPM, drop on the chorus hit)",
   segs=[(0,1.917,4),(1.917,2.958,2),(2.958,3.833,2),(3.833,4.833,2),(5.417,6.417,2),(6.833,7.833,2),
         (9.6,10.6,2),(11.25,12.458,2),(12.458,14.042,4),(14.042,15.167,4)],
   flash=[16], slowzoom=[(22,26)],
   caps=[(4,10,"strap on.",None),(4,10,"PRESS ONCE.",YEL),
         (10,16,"3 HEAT LEVELS",YEL),
         (16,22,"then walk out",None),(16,22,"INTO THE SNOW",YEL),
         (22,26,"warm hands all winter",None),(22,26,"LINK IN BIO",YEL)]),
 "v3_heatup": dict(src=UP+"3727053c-VID-20261112-WA0002.mp4", bpm=107, beat="beats/beat_v3_reveal_107bpm.wav",
   song="Last Christmas - Wham! (107 BPM)",
   segs=[(0,.833,2),(.833,1.792,2),(1.792,2.875,2),(2.875,3.958,2),(3.958,5.1,2),(5.4,6.5,2),
         (7.375,8.5,2),(9.0,10.1,2),(10.4,11.6,2),(11.667,12.8,2),(13.458,15.15,4)],
   flash=[4], slowzoom=[(20,24)],
   caps=[(4,8,"yes.",None),(4,8,"HEATED GLOVES",YEL),
         (8,12,"fit like",None),(8,12,"NORMAL GLOVES",YEL),
         (12,18,"don't need the coffee",None),(12,18,"TO WARM UP ANYMORE",YEL),
         (18,24,"best winter buy",None),(18,24,"LINK IN BIO",YEL)]),
}
def esc(s): return s.replace("\\","\\\\").replace("'", "’").replace(":", "\\:").replace(",", "\\,")
def build(name, v):
    b = 60 / v["bpm"]; parts = []; fc = []; cuts = []; acc = 0
    for k, (a, e, nb) in enumerate(v["segs"]):
        d = nb * b; sp = (e - a) / d; cuts.append(acc * b); acc += nb
        fc.append(f"[0:v]trim={a}:{e},setpts=(PTS-STARTPTS)/{sp:.5f},fps=30,"
                  f"scale=1080:1890:flags=lanczos,crop=1080:1890,pad=1080:1920:0:15,setsar=1,trim=0:{d:.5f}[s{k}]")
        aa = f"[0:a]atrim={a}:{e},asetpts=PTS-STARTPTS"
        aa += ("," + ",".join([f"atempo={min(max(sp,0.5),2.0):.5f}"])) + f",apad,atrim=0:{d:.5f}[a{k}]"
        fc.append(aa)
    N = len(v["segs"]); total = acc * b
    fc.append("".join(f"[s{k}][a{k}]" for k in range(N)) + f"concat=n={N}:v=1:a=1[cv][ca]")
    # punch-in zoom on every cut (decays over 0.22s), plus slow push-in on outro beats
    zs = [f"0.09*max(0\\,1-(t-{c:.4f})/0.22)*gte(t\\,{c:.4f})" for c in cuts[1:]]
    sz = "+".join(f"0.06*between(t\\,{s*b:.3f}\\,{e*b:.3f})*(t-{s*b:.3f})/{(e-s)*b:.3f}" for s, e in v["slowzoom"])
    Z = f"(1+{'+'.join(zs)}+{sz})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,"
              f"crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.06:saturation=1.12[zv]")
    # flash on the drop beat(s)
    flt = "+".join(f"0.85*max(0\\,1-(T-{f*b:.4f})/0.18)*gte(T\\,{f*b:.4f})" for f in v["flash"])
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,"
              f"geq=r=255:g=255:b=255:a='255*({flt})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[fv]")
    # beat-timed captions (two-line stacks, pop-in)
    dt = []; rows = {}
    for s, e, txt, col in v["caps"]:
        r = rows.get((s, e), 0); rows[(s, e)] = r + 1
        y = 1335 + r * 92; fs = 64 if col is None else 82
        t0 = s * b; t1 = e * b
        dt.append(f"drawtext=fontfile={FONT}:text='{esc(txt)}':fontsize={fs}:fontcolor={col or 'white'}:"
                  f"borderw=7:bordercolor=black@0.95:shadowx=0:shadowy=5:shadowcolor=black@0.5:"
                  f"x=(w-text_w)/2:y={y}+18*max(0\\,1-(t-{t0:.3f})/0.12):"
                  f"alpha='min(1\\,(t-{t0:.3f})/0.08)':enable='between(t\\,{t0:.3f}\\,{t1:.3f})'")
    fc.append("[fv]" + ",".join(dt) + ",format=yuv420p[v]")
    common = ["-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
              "-r", "30", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "44100"]
    # A) TRENDSOUND: natural foley only (add trending sound in-app)
    fa = ";".join(fc) + ";[ca]loudnorm=I=-16:TP=-1.5,atrim=0:" + f"{total:.4f}[aout]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v["src"], "-filter_complex", fa, *common,
                    "-map", "[aout]", f"{OUT}/{name}_TRENDSOUND.mp4"], check=True, cwd=W)
    # B) READY: original beat + foley ducked under it
    fb = ";".join(fc) + (f";[1:a]atrim=0:{total+0.6:.4f},afade=t=out:st={total+0.1:.3f}:d=0.5,volume=1.0[m];"
          f"[ca]volume=0.28,apad[fx];[m][fx]amix=inputs=2:duration=first:normalize=0,"
          f"loudnorm=I=-14:TP=-1.0[aout]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v["src"], "-i", v["beat"], "-filter_complex", fb,
                    *common, "-map", "[aout]", "-t", f"{total+0.6:.3f}", f"{OUT}/{name}_READY.mp4"], check=True, cwd=W)
    print(name, f"{total:.2f}s", "cuts@", [round(c, 3) for c in cuts])
for k, v in VIDS.items():
    if len(sys.argv) < 3 or k in sys.argv[2:]: build(k, v)
