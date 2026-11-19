"""9 German HoHoHound Reels from a 16-clip library, in the competitor format:
persistent native-style hook text + 'Ich:' line, store/hook clip before the music hit,
then a fast multi-breed montage cut on the beat.  python3 hohohound_9.py [name ...]"""
import json, subprocess, sys, re, os, numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/user/aureveile/edits/hohohound/raw/"          # s01.mp4 .. s16.mp4
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/hh/ov/"
OUTD = "/home/user/aureveile/edits/hohohound/9_reels/"
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
SONGS = {"mariah": ("9d88af6e-All_I_Want_for_Christmas_Is_You.mp3", "v1_gift", 49.760),
         "lastxmas": ("09c4c148-Last_Christmas.mp3", "v3_heatup", 7.709),
         "housewife": ("27fc37e0-Housewife.mp3", "v2_coldhands", 37.198)}
BEATS = json.load(open("/home/user/aureveile/edits/tools/songbeats.json"))
FT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 54)
FB = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 150)
FE = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"

# clip library: id -> default source start (s)
LIB = {1: 0.6, 2: 0.2, 3: 0.0, 4: 0.3, 5: 0.2, 6: 0.3, 7: 0.3, 8: 0.2, 9: 0.2, 10: 0.2, 11: 0.2, 12: 0.3, 13: 0.0, 14: 0.2, 15: 0.3, 16: 0.2}

def is_emo(ch): return ord(ch) >= 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF
def runs(s):
    out = []
    for ch in s:
        if ch == "\ufe0f": continue
        e = is_emo(ch)
        if out and out[-1][0] == e and not e: out[-1][1] += ch
        else: out.append([e, ch])
    return out

def render(lines, path, font=FT, align="center", stroke=5):
    """lines of text with inline emoji -> transparent 1080-wide PNG (TikTok-native look)."""
    lh = int(font.size * 1.28); es = int(font.size * 1.08)
    im = Image.new("RGBA", (1080, lh * len(lines) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, line in enumerate(lines):
        parts = runs(line); w = 0; widths = []
        for e, t in parts:
            pw = es + 4 if e else int(d.textlength(t, font=font)); widths.append(pw); w += pw
        x = (1080 - w) // 2 if align == "center" else 60; y = 12 + li * lh
        for (e, t), pw in zip(parts, widths):
            if e:
                g = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(g).text((0, 0), t, font=FE, embedded_color=True)
                g = g.crop(g.getbbox()).resize((es, es), Image.LANCZOS); im.alpha_composite(g, (x + 2, y + int(font.size * 0.02)))
            else:
                d.text((x, y), t, font=font, fill="white", stroke_width=stroke, stroke_fill=(0, 0, 0, 235))
            x += pw
    im.save(path); return path

# name: song, pre (clip, src_start, seconds before hit), montage [(clip, beats)], hook lines, ich line, extras
R = {
 "01_Schatz_Montage": dict(song="mariah", pre=(5, 0.2, 2.8), mont=[(6, 5), (7, 5), (3, 5), (11, 5), (9, 5), (8, 5), (10, 6)],
     hook=["„Schatz, der Hund braucht", "das nicht.“ 🙄"], ich="Ich: 😍🎄", ich_at=1.2),
 "02_Hundemama": dict(song="lastxmas", pre=(1, 0.6, 2.6), mont=[(2, 4), (3, 4), (12, 4), (16, 4), (11, 4), (9, 4), (10, 4)],
     hook=["Zeig das bloß keiner", "Hundemama… 🤭🎄"]),
 "03_Rasse_Voting": dict(song="mariah", pre=(7, 0.3, 1.8), mont=[(8, 5), (9, 5), (3, 5), (11, 5), (12, 5), (16, 5), (14, 5)],
     hook=["Welche Rasse trägt es", "am besten? 🤔👇"], numbers=True),
 "04_Mann_NICHTS": dict(song="lastxmas", pre=(1, 0.6, 3.2), mont=[(14, 5), (3, 4), (13, 4), (4, 5)],
     hook=["Mein Mann: „Wir kaufen dem Hund", "NICHTS zu Weihnachten.“"], ich="Der Hund an Heiligabend: 🎅", ich_at=1.6, ich_from_hit=True),
 "05_POV_Reiter": dict(song="housewife", pre=(13, 1.5, 3.0), mont=[(7, 4), (9, 4), (16, 4), (3, 4), (11, 4), (10, 5)],
     hook=["POV: Dein Hund merkt, dass", "jemand auf ihm reitet 😳"]),
 "06_Oma_lacht": dict(song="mariah", pre=(14, 0.2, 2.8), mont=[(6, 5), (3, 5), (12, 5), (8, 5), (4, 7)],
     hook=["Oma hat Tränen gelacht 😂🎄"]),
 "07_Jeder_Hund": dict(song="lastxmas", pre=(15, 0.3, 3.0), mont=[(7, 4), (8, 4), (12, 4), (16, 4), (11, 4), (4, 5)],
     hook=["Jeder Hund verdient so ein", "Weihnachten 🥹🎄"]),
 "08_Zwei_Hunde": dict(song="mariah", pre=(10, 0.2, 2.6), mont=[(9, 5), (3, 5), (11, 5), (7, 5), (10, 6)],
     hook=["Wenn du ZWEI Hunde hast,", "brauchst du das zweimal 😂🎅"]),
 "09_Weihnachtsmarkt": dict(song="lastxmas", pre=(12, 0.3, 2.6), mont=[(8, 4), (16, 4), (7, 4), (2, 4), (4, 5)],
     hook=["Wir waren mit ihm auf dem", "Weihnachtsmarkt… 🎄"], ich="Jeder wollte ein Foto 📸", ich_at=0.0, ich_from_hit=True),
}
CTA = ["Schreib „SANTA“ für den Link 👇"]

def build(name, cfg, gain, out):
    song, key, hit = SONGS[cfg["song"]]; bt = np.array(BEATS[key]["beats"]); i0 = int(np.argmin(abs(bt - hit)))
    pc, ps, PRE = cfg["pre"]; B = lambda k: PRE + float(bt[i0 + k] - bt[i0])
    ins = [SRC + f"s{pc:02d}.mp4"] + [SRC + f"s{c:02d}.mp4" for c, _ in cfg["mont"]]
    fc = [f"[0:v]trim={ps}:{ps + PRE * 1.0:.3f},setpts=PTS-STARTPTS,fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{PRE:.4f}[p]"]
    labels = ["[p]"]; cuts = [0.0, PRE]; k = 0
    for i, (c, nb) in enumerate(cfg["mont"]):
        d = B(k + nb) - B(k); s0 = LIB[c]; sp = 1.12 if s0 + d * 1.12 <= 4.95 else (4.95 - s0) / d
        fc.append(f"[{i+1}:v]trim={s0}:{s0 + d * sp:.3f},setpts=(PTS-STARTPTS)/{sp:.4f},fps=30,{SC},tpad=stop_mode=clone:stop_duration=1,trim=0:{d:.4f},setpts=PTS-STARTPTS[c{i}]")
        labels.append(f"[c{i}]"); k += nb; cuts.append(B(k))
    total = cuts[-1]; n = len(ins)
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cv]")
    zs = "+".join(f"0.06*max(0\\,1-(t-{c:.3f})/0.18)*gte(t\\,{c:.3f})" for c in cuts[1:-1])
    Z = f"(1+0.03*max(0\\,1-t/0.3)+{zs})"
    fc.append(f"[cv]scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.02:saturation=1.05[zv]")
    fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.45*max(0\\,1-(T-{PRE:.3f})/0.14)*gte(T\\,{PRE:.3f})'[fl]")
    fc.append("[zv][fl]overlay=0:0:shortest=1[v0]")
    # overlays: (png, x, y, t0, t1)
    ov = [(render(cfg["hook"], TMP + f"{name}_hook.png"), 0, 230, 0, total + 1)]
    if cfg.get("ich"):
        t0 = (PRE if cfg.get("ich_from_hit") else 0) + cfg["ich_at"]
        ov.append((render([cfg["ich"]], TMP + f"{name}_ich.png", align="left"), 0, 940, t0, total + 1))
    if cfg.get("numbers"):
        for j in range(len(cuts) - 1):
            ov.append((render([str(j + 1)], TMP + f"{name}_n{j}.png", font=FB, align="left", stroke=9), 0, 1420, cuts[j], cuts[j + 1]))
    cta_t = cuts[-2] + 0.25
    ov.append((render(CTA, TMP + f"{name}_cta.png"), 0, 1540, cta_t, total + 1))
    cur = "[v0]"; extra = []
    for j, (png, x, y, t0, t1) in enumerate(ov):
        extra += ["-loop", "1", "-i", png]; idx = n + j; nxt = f"[o{j}]"
        fc.append(f"{cur}[{idx}:v]overlay=x={x}:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1 - 0.034:.3f})':shortest=0:eof_action=pass{nxt}")
        cur = nxt
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    aidx = n + len(ov); L = total
    fc.append(f"[{aidx}:a]atrim=0:{L:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={L-0.45:.3f}:d=0.45,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    args = sum([["-i", f] for f in ins], []) + extra + ["-ss", f"{bt[i0] - PRE - 0.015:.3f}", "-i", U + song]
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "slow", "-crf", "18", "-maxrate", "8M", "-bufsize", "16M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{L:.3f}", out],
        capture_output=True, text=True)
    if r.returncode: print(name, r.stderr[-2000:]); sys.exit(1)
    return cuts

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
    for name in (sys.argv[1:] or R):
        out = OUTD + f"HoHoHound_{name}.mp4"
        build(name, R[name], 0, out)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        cuts = build(name, R[name], round(-14 - I, 1), out)
        print("OK", name, round(cuts[-1], 2), "s")
