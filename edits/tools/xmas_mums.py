"""20 HoHoHound Facebook Reels for German 'Weihnachts-Mamas', cut from clips we already have (no new generation).
Christmas songs only. Every reel: niche hook on frame 0, one mass desire (a magical Christmas the whole family
remembers, dog included), a different edit style, CTA „MAMA“ at the end, -14 LUFS.
python3 xmas_mums.py [R01 R02 ...]"""
import json, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render, runs, FT, FB, FE

E = "/home/user/aureveile/edits/"
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
OUT = E + "hohohound/xmas_mums/"
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/xm/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"

C = {f"s{i:02d}": E + f"hohohound/raw/s{i:02d}.mp4" for i in range(1, 17)}
C.update({f"p{i}": E + f"hohohound/premium/p{i}_{n}.mp4" for i, n in
          enumerate(["store", "shelf", "unbox", "dress", "trot", "him", "labs", "sleep"], 1)})
C.update({"hb": E + "scout_reels/clips/h_burst.mp4", "hd": E + "scout_reels/clips/h_door.mp4", "hf": E + "scout_reels/clips/h_family.mp4",
          "h2": E + "scout_reels/clips/h2_seedance.mp4", "h3": E + "scout_reels/clips/h3_seedance.mp4", "h4": E + "scout_reels/clips/h4_seedance.mp4"})
C.update({f"H{i}": E + f"niche_reels/clips/H{i}.mp4" for i in range(1, 8)})

# Christmas songs only: file, anchor (a strong beat to start on)
SONG = {"aiw": ("9d88af6e-All_I_Want_for_Christmas_Is_You.mp3", 49.76),
        "lc": ("09c4c148-Last_Christmas.mp3", 7.709),
        "lcp": ("fc628e28-Last_Christmas_-_Pudding_Mix.mp3", None),
        "sr": ("e73f2714-Sleigh_Ride.mp3", 4.11),
        "sr1": ("b52e4c65-Sleigh_Ride_1.mp3", None),
        "cb": ("115c4178-Christmas_Baby_Please_Come_Home.mp3", 12.12)}
BC = TMP + "beats.json"
CTA = ["Schreib „MAMA“ für den Link 👇"]

def beats_of(key):
    cache = json.load(open(BC)) if os.path.exists(BC) else {}
    if key not in cache:
        import librosa
        y, sr = librosa.load(U + SONG[key][0], sr=22050, mono=True)
        _, b = librosa.beat.beat_track(y=y, sr=sr, units="time")
        anchor = SONG[key][1]
        if anchor is None:  # loudest 14 s, snapped to a beat
            rms = librosa.feature.rms(y=y, hop_length=512)[0]; t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
            w = int(14 * sr / 512); cs = np.convolve(rms, np.ones(w), "valid"); cs[t[:len(cs)] > len(y) / sr - 16] = 0
            anchor = float(t[int(np.argmax(cs))])
        cache[key] = dict(beats=[float(x) for x in b], anchor=anchor)
        json.dump(cache, open(BC, "w"))
    return np.array(cache[key]["beats"]), cache[key]["anchor"]

from PIL import ImageFont
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def line_w(line, font):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10))); es = int(font.size * 1.08)
    return sum(es + 4 if e else int(d0.textlength(t, font=font)) for e, t in runs(line))
def fitted(lines, size, maxw):
    while size > 34 and max(line_w(l, ImageFont.truetype(INTER_B, size)) for l in lines) > maxw: size -= 2
    return ImageFont.truetype(INTER_B, size)

def render_box(lines, path, font=None):
    """black text on a white rounded box (TikTok/Reels caption look)"""
    font = font or fitted(lines, 62, 960)
    lh = int(font.size * 1.3); es = int(font.size * 1.05); pad = 26
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    widths = [sum(es + 4 if e else int(d0.textlength(t, font=font)) for e, t in runs(l)) for l in lines]
    W = max(widths) + 2 * pad; H = lh * len(lines) + 2 * pad - 10
    im = Image.new("RGBA", (1080, H + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = (1080 - W) // 2; d.rounded_rectangle([x0, 4, x0 + W, 4 + H], 24, fill=(255, 255, 255, 245))
    for li, (line, w) in enumerate(zip(lines, widths)):
        x = (1080 - w) // 2; y = 4 + pad - 6 + li * lh
        for e, t in runs(line):
            if e:
                g = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(g).text((0, 0), t, font=FE, embedded_color=True)
                g = g.crop(g.getbbox()).resize((es, es), Image.LANCZOS); im.alpha_composite(g, (x + 2, y + 4)); x += es + 4
            else:
                d.text((x, y), t, font=font, fill=(17, 17, 17)); x += int(d.textlength(t, font=font))
    im.save(path); return path

def render_big(text, path):
    im = Image.new("RGBA", (1080, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = d.textlength(text, font=FB); d.text(((1080 - w) / 2, 30), text, font=FB, fill="white", stroke_width=9, stroke_fill=(0, 0, 0, 240))
    im.save(path); return path

# ---------------------------------------------------------------- the 20 reels
# seg: (clip, src_start, dur, opts)  dur = beats when beat=True else seconds
# opts: sp speed · freeze=s of motion then hold · kb=slow push-in · split=(clip,start) bottom half · grid=[(clip,start)]*3 extra quadrants
# text: (lines, pos, from_seg, to_seg_incl | None=end, style)  pos top/mid/bot/int · style s(troke)/b(ox)/big
R = {
 "R01": dict(title="Stopp-Hook Beat-Montage", song="aiw", beat=True, punch=True, segs=[
    ("p5", 0.6, 2, {}), ("H1", 4.0, 2, {}), ("s03", 0.5, 2, {}), ("H2", 2.0, 2, {}), ("p7", 0.4, 2, {}),
    ("H4", 6.5, 2, {}), ("H6", 5.0, 2, {}), ("hb", 0.3, 2, {}), ("H3", 2.5, 3, {})],
    text=[(["Weihnachts-Mamas, STOPP 🛑"], "top", 0, 0, "b"), (["Das fehlt dieses Jahr", "noch unterm Baum 🎄"], "top", 1, None, "b")]),
 "R02": dict(title="Weihnachts-Mama-Checkliste", song="sr", beat=True, punch=True, segs=[
    ("p5", 0.2, 3, {}), ("s14", 0.3, 3, {}), ("hf", 0.3, 3, {}), ("s03", 0.3, 3, {}), ("H2", 7.0, 4, {})],
    text=[(["Weihnachts-Mama-Checkliste 2026 🎄"], "top", 0, None, "b"),
          (["Baum geschmückt ✅"], 560, 0, 0, "s"), (["Baum geschmückt ✅", "Familienessen geplant ✅"], 560, 1, 1, "s"),
          (["Baum geschmückt ✅", "Familienessen geplant ✅", "Geschenke verpackt ✅"], 560, 2, 2, "s"),
          (["Baum geschmückt ✅", "Familienessen geplant ✅", "Geschenke verpackt ✅", "Hund als Weihnachtsmann ✅"], 560, 3, 3, "s"),
          (["…und als Weihnachtsbaum ✅🎄"], 560, 4, None, "s")]),
 "R03": dict(title="Slow-Mo Gänsehaut-Reveal", song="cb", beat=False, punch=False, grade="warm", segs=[
    ("H1", 0.0, 2.4, {"sp": 0.8}), ("H1", 4.0, 4.6, {"sp": 0.65}), ("H1", 8.0, 3.4, {"sp": 0.6})],
    text=[(["Für alle Mamas, die Weihnachten", "jedes Jahr magisch machen 🥹"], "top", 0, 1, "s"),
          (["Genau DAS ist der Moment ❤️"], "top", 2, None, "s")]),
 "R04": dict(title="Erwartung vs. Realität (Split-Screen)", song="sr1", beat=False, punch=False, segs=[
    ("H7", 0.0, 10.5, {"sp": 0.92, "split": ("H7", 2.0), "top_sp": 0.15})],
    text=[(["Mein Plan als Weihnachts-Mama 📸"], 120, 0, None, "b"), (["Die Realität 😂"], 1060, 0, None, "b")]),
 "R05": dict(title="2×2-Voting-Grid", song="aiw", beat=False, punch=False, segs=[
    ("p5", 0.0, 10.5, {"sp": 0.48, "grid": [("H2", 4.0), ("H4", 5.0), ("H6", 5.0)]})],
    text=[(["Weihnachts-Mamas, ehrlich:", "Welcher ist euer Favorit? 👇"], 800, 0, None, "b")], numbers=True),
 "R06": dict(title="Foto-Blitz-Momente", song="lc", beat=True, punch=False, flash=True, segs=[
    ("hf", 0.4, 3, {"freeze": 1.3}), ("s14", 0.4, 3, {"freeze": 1.3}), ("H3", 8.6, 3, {"freeze": 1.0}),
    ("p8", 0.5, 3, {"freeze": 1.3}), ("H1", 8.2, 4, {"freeze": 1.6})],
    text=[(["Fotos, die eine Weihnachts-Mama", "jedes Jahr wieder anschaut 📸"], "top", 0, None, "s")]),
 "R07": dict(title="Reverse-Open Story", song="cb", beat=False, punch=True, segs=[
    ("H1", 8.0, 2.0, {}), ("H1", 0.0, 4.0, {}), ("H1", 4.0, 4.0, {}), ("H1", 8.0, 2.0, {})],
    text=[(["Warum weint Mama", "an Heiligabend? 🥹"], "top", 0, 0, "b"), (["Ein paar Sekunden vorher…"], "top", 1, 1, "b"),
          (["Erstes Weihnachten mit", "unserem Tierschutzhund 🎄"], "top", 2, None, "b")]),
 "R08": dict(title="Eine Sache geändert", song="lcp", beat=True, punch=True, segs=[
    ("p4", 0.5, 4, {}), ("p5", 0.6, 4, {}), ("s14", 0.3, 4, {}), ("hf", 0.3, 4, {})],
    text=[(["Ich habe als Mama EINE Sache", "an Weihnachten geändert…"], "top", 0, 1, "s"),
          (["…und plötzlich haben ALLE", "gelacht 😂🎄"], "top", 2, None, "s")]),
 "R09": dict(title="Speed-Ramp Sprung", song="sr", beat=False, punch=True, segs=[
    ("H5", 1.0, 1.5, {"sp": 1.6}), ("H5", 4.4, 3.2, {"sp": 0.45}), ("H5", 7.0, 2.4, {}), ("H4", 5.6, 3.2, {})],
    text=[(["Weihnachts-Mamas, wenn der Hund", "sein Kostüm zum 1. Mal trägt 👀"], "top", 0, None, "s")]),
 "R10": dict(title="Dinge, die nur Weihnachts-Mamas verstehen", song="lc", beat=True, punch=True, segs=[
    ("H3", 2.0, 5, {}), ("H7", 0.0, 5, {}), ("p5", 0.4, 5, {}), ("H2", 7.0, 6, {})],
    text=[(["Dinge, die nur", "Weihnachts-Mamas verstehen 🎄"], "top", 0, None, "b"),
          (["1. Der Hund kriegt mehr", "Geschenke als du 🎁"], 1250, 0, 0, "s"), (["2. Das Familienfoto ist", "seit Oktober geplant 📸"], 1250, 1, 1, "s"),
          (["3. Der Star ist trotzdem", "der Hund 🐶"], 1250, 2, 2, "s"), (["4. …im passenden Kostüm 😍"], 1250, 3, None, "s")]),
 "R11": dict(title="Cinematic Heiligabend (Letterbox)", song="cb", beat=False, punch=False, letterbox=True, grade="warm", segs=[
    ("s11", 0.3, 2.6, {"kb": 1}), ("p8", 0.4, 2.8, {"kb": 1}), ("s15", 0.3, 2.6, {"kb": 1}), ("h4", 10.0, 2.0, {"kb": 1}), ("s16", 0.3, 3.0, {"kb": 1})],
    text=[(["Für Mamas, die Weihnachten", "von Herzen lieben 🎄❤️"], 120, 0, None, "s"), (["Heiligabend 2026"], 1700, 0, 1, "s")]),
 "R12": dict(title="POV Paket-Story", song="sr1", beat=False, punch=True, segs=[
    ("H6", 0.0, 3.0, {}), ("H6", 3.0, 2.4, {}), ("H6", 5.4, 4.6, {})],
    text=[(["POV: Du bist die Weihnachts-Mama", "und hast heimlich bestellt 🤫"], "top", 0, None, "b"),
          (["Paket ist da 📦"], 1300, 0, 0, "s"), (["Der Hund ist schneller als du 😂"], 1300, 1, 1, "s"),
          (["Bester Weihnachtsbaum im Haus 🎄"], 1300, 2, None, "s")]),
 "R13": dict(title="Vorher/Nachher-Flash", song="lcp", beat=True, punch=True, flash=True, segs=[
    ("H4", 0.2, 3, {}), ("H4", 7.0, 4, {}), ("H6", 0.0, 3, {}), ("H6", 7.2, 4, {}), ("H2", 7.6, 4, {})],
    text=[(["Weihnachts-Mamas, macht das", "mit eurem Hund 😍"], "top", 0, None, "b"),
          (["Vorher 🐶"], 1250, 0, 0, "s"), (["Nachher 🎄"], 1250, 1, 1, "s"), (["Vorher 🐶"], 1250, 2, 2, "s"), (["Nachher 🎄"], 1250, 3, None, "s")]),
 "R14": dict(title="Santa-vs-Baum Ping-Pong", song="aiw", beat=True, punch=True, segs=[
    ("s03", 0.4, 2, {}), ("H2", 2.0, 2, {}), ("p7", 0.4, 2, {}), ("H4", 6.5, 2, {}), ("s09", 0.3, 2, {}), ("H6", 6.0, 2, {}), ("p5", 1.5, 2, {}), ("H1", 4.5, 3, {})],
    text=[(["Mamas, ehrlich:", "Santa 🎅 oder Tannenbaum 🎄?"], "top", 0, None, "b"),
          (["🎅"], 1250, 0, 0, "s"), (["🎄"], 1250, 1, 1, "s"), (["🎅"], 1250, 2, 2, "s"), (["🎄"], 1250, 3, 3, "s"),
          (["🎅"], 1250, 4, 4, "s"), (["🎄"], 1250, 5, 5, "s"), (["🎅"], 1250, 6, 6, "s"), (["Schreib 1 oder 2 👇"], 1250, 7, None, "s")]),
 "R15": dict(title="Finde den 2. Baum (Loop)", song="sr", beat=False, punch=False, segs=[
    ("H2", 0.0, 10.0, {}), ("H2", 0.0, 0.8, {})],
    text=[(["Mamas, findet den zweiten", "Weihnachtsbaum 🎄👀"], "top", 0, None, "s")]),
 "R16": dict(title="3-2-1 Countdown", song="lc", beat=True, punch=True, segs=[
    ("H1", 4.0, 6, {}), ("s14", 0.3, 6, {}), ("H3", 7.6, 6, {})],
    text=[(["3 Gründe, warum Weihnachts-Mamas", "das hier lieben 🎄"], "top", 0, None, "s"),
          (["3"], 700, 0, 0, "big"), (["Die Kinder flippen aus 🤩"], 980, 0, 0, "b"),
          (["2"], 700, 1, 1, "big"), (["Oma lacht Tränen 😂"], 980, 1, 1, "b"),
          (["1"], 700, 2, None, "big"), (["Die schönsten Fotos des Jahres 📸"], 980, 2, None, "b")]),
 "R17": dict(title="Weihnachtsmarkt-Auflauf", song="sr1", beat=False, punch=True, segs=[
    ("h2", 2.2, 3.6, {}), ("h2", 6.0, 2.0, {}), ("s12", 0.3, 2.6, {}), ("h2", 9.6, 2.4, {})],
    text=[(["Weihnachts-Mamas auf dem", "Weihnachtsmarkt be like 😂"], "top", 0, None, "s"),
          (["Alle wollten ein Foto 📸"], 1300, 2, None, "b")]),
 "R18": dict(title="Mamas Dezember-Mental-Load (Wort-pro-Beat)", song="aiw", beat=True, punch=True, segs=[
    ("hf", 0.3, 2, {}), ("p8", 0.4, 2, {}), ("H7", 0.0, 2, {}), ("p3", 0.4, 2, {}), ("p4", 0.6, 2, {}), ("p5", 0.6, 4, {})],
    text=[(["Was Mama im Dezember", "alles organisiert:"], "top", 0, None, "s"),
          (["Geschenke 🎁"], 860, 0, 0, "big_t"), (["Deko 🎄"], 860, 1, 1, "big_t"), (["Familienfoto 📸"], 860, 2, 2, "big_t"),
          (["Paket 📦"], 860, 3, 3, "big_t"), (["Kostüm an 🎅"], 860, 4, 4, "big_t"), (["…und alle lieben es ❤️"], 860, 5, None, "big_t")]),
 "R19": dict(title="Opa-Moment mit Überblendungen", song="cb", beat=False, punch=False, dissolve=True, grade="warm", segs=[
    ("h4", 0.3, 3.4, {}), ("h4", 4.2, 2.2, {}), ("h4", 6.4, 3.2, {}), ("h4", 9.8, 2.2, {}), ("s14", 0.3, 2.6, {})],
    text=[(["Weihnachts-Mamas wissen:", "Das schönste Geschenk", "ist Opas Lächeln 🥹"], "top", 0, None, "s")]),
 "R20": dict(title="1… 2… 3 Hunde (Zähl-Punches)", song="sr", beat=True, punch=True, segs=[
    ("H3", 2.0, 3, {}), ("H3", 4.0, 3, {}), ("H3", 6.0, 3, {}), ("p7", 0.4, 4, {}), ("H3", 8.0, 4, {})],
    text=[(["Für Mamas mit mehr als", "einem Hund 🐶🐶🐶"], "top", 0, None, "b"),
          (["1…"], 800, 0, 0, "big"), (["2…"], 800, 1, 1, "big"), (["3!"], 800, 2, 2, "big"),
          (["Ab 2 Kostümen 15 % sparen 🎄"], 1250, 3, None, "s")]),
}

def ff(args):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2500:]); sys.exit(1)

def fit(sp, s, d, w=1080, h=1920):
    sc = f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},setsar=1"
    return f"trim={s}:{s + d * sp + 0.2:.3f},setpts=(PTS-STARTPTS)/{sp},fps=30,{sc},tpad=stop_mode=clone:stop_duration=3,trim=0:{d:.4f},setpts=PTS-STARTPTS"

REUSE = False
def seg_file(name, k, seg, d, extra):
    clip, s, _, o = seg; sp = o.get("sp", 1.0); out = TMP + f"{name}_{k}.mp4"; d2 = d + extra
    if REUSE and os.path.exists(out): return out
    if "split" in o:
        c2, s2 = o["split"]; tsp = o.get("top_sp", 1.0)
        fc = f"[0:v]{fit(tsp, s, d2, 1080, 960)}[a];[1:v]{fit(sp, s2, d2, 1080, 960)}[b];[a][b]vstack,drawbox=y=956:w=1080:h=8:color=white:t=fill[v]"
        ff(["-i", C[clip], "-i", C[c2], "-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out]); return out
    if "grid" in o:
        q = [(clip, s)] + o["grid"]; ins = sum([["-i", C[c]] for c, _ in q], [])
        fc = ";".join(f"[{i}:v]{fit(sp, st, d2, 540, 960)}[q{i}]" for i, (_, st) in enumerate(q))
        fc += ";[q0][q1][q2][q3]xstack=inputs=4:layout=0_0|540_0|0_960|540_960,drawbox=x=536:w=8:h=1920:color=white:t=fill,drawbox=y=956:w=1080:h=8:color=white:t=fill[v]"
        ff(ins + ["-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out]); return out
    if "freeze" in o:
        m = o["freeze"]; vf = fit(sp, s, m) + f",tpad=stop_mode=clone:stop_duration={d2 - m + 0.1:.3f},trim=0:{d2:.4f}"
    else:
        vf = fit(sp, s, d2)
    if o.get("kb"):
        vf += f",scale=w='trunc(1080*(1+0.07*t/{d2:.2f})/2)*2':h='trunc(1920*(1+0.07*t/{d2:.2f})/2)*2':eval=frame:flags=bicubic,crop=1080:1920"
    ff(["-i", C[clip], "-vf", vf, "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out]); return out

def text_png(name, j, lines, style):
    p = TMP + f"{name}_t{j}.png"
    if style == "b": return render_box(lines, p)
    if style == "big": return render_big(lines[0], p)
    if style == "big_t":
        from PIL import ImageFont
        return render(lines, p, font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 92), stroke=7)
    return render(lines, p, font=fitted(lines, 58, 1010))

def build(name, gain):
    cfg = R[name]; key = cfg["song"]; bt, anchor = beats_of(key)
    if cfg["beat"]:
        i0 = int(np.argmin(abs(bt - anchor))); a0 = float(bt[i0]); cum = np.cumsum([0] + [sg[2] for sg in cfg["segs"]])
        bounds = [float(bt[i0 + int(c)] - bt[i0]) for c in cum]
    else:
        a0 = anchor; bounds = list(np.cumsum([0.0] + [sg[2] for sg in cfg["segs"]]))
    durs = np.diff(bounds); ov = 0.5 if cfg.get("dissolve") else 0.0
    files = [seg_file(name, k, sg, float(durs[k]), ov) for k, sg in enumerate(cfg["segs"])]
    total = bounds[-1]
    ins = sum([["-i", f] for f in files], []); n = len(files)
    if ov:
        chain = "[0:v]"; off = 0.0; fc = []
        for k in range(1, n):
            off += durs[k - 1]; lab = f"[x{k}]"
            fc.append(f"{chain}[{k}:v]xfade=transition=fade:duration={ov}:offset={off:.3f}{lab}"); chain = lab
        # xfade shortens each join by ov: compensate by holding tail
        fc.append(f"{chain}tpad=stop_mode=clone:stop_duration=2,trim=0:{total:.3f}[cv]")
    else:
        fc = ["".join(f"[{k}:v]" for k in range(n)) + f"concat=n={n}:v=1:a=0[cv]"]
    cuts = bounds[1:-1]
    post = []
    if cfg.get("punch") and cuts:
        zs = "+".join(f"0.06*max(0\\,1-(t-{x:.3f})/0.18)*gte(t\\,{x:.3f})" for x in cuts)
        post.append(f"scale=w='trunc(1080*(1+{zs})/2)*2':h='trunc(1920*(1+{zs})/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2")
    if cfg.get("grade") == "warm": post.append("colorbalance=rs=0.04:gs=0.01:bs=-0.04:rm=0.03:bm=-0.03,eq=contrast=1.03:saturation=1.06")
    else: post.append("eq=contrast=1.03:saturation=1.04")
    post.append("unsharp=5:5:0.35")
    if cfg.get("letterbox"): post.append("drawbox=y=0:w=1080:h=210:color=black:t=fill,drawbox=y=1710:w=1080:h=210:color=black:t=fill")
    fc.append("[cv]" + ",".join(post) + "[v0]")
    cur = "[v0]"; extra = []; idx = n
    if cfg.get("flash"):
        ft = [b + cfg["segs"][k][3].get("freeze", 0) for k, b in enumerate(bounds[:-1])]
        fl = "+".join(f"0.75*max(0\\,1-(T-{x:.3f})/0.16)*gte(T\\,{x:.3f})" for x in ft if x > 0.05) or "0"
        fc.append(f"color=white:s=1080x1920:r=30:d={total:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*min(1\\,{fl})'[fl]")
        fc.append(f"{cur}[fl]overlay=0:0:shortest=1[vf]"); cur = "[vf]"
    if cfg.get("numbers"):
        for j, (x, y) in enumerate([(30, 30), (570, 30), (30, 990), (570, 990)]):
            p = render_big(str(j + 1), TMP + f"{name}_n{j}.png"); extra += ["-loop", "1", "-i", p]
            fc.append(f"{cur}[{idx}:v]overlay=x={x - 440}:y={y - 20}:enable='lt(t\\,{total:.3f})'[n{j}]"); cur = f"[n{j}]"; idx += 1
    POS = {"top": 200, "mid": 860, "bot": 1460}
    tx = cfg["text"] + [(CTA, 1500 if not cfg.get("letterbox") else 1440, None, None, "b")]
    for j, (lines, pos, a, b, style) in enumerate(tx):
        if a is None: t0, t1 = total - 2.6, total + 1
        else: t0 = bounds[a] + (0.08 if a else 0); t1 = (bounds[b + 1] if b is not None else total + 1)
        y = POS.get(pos, pos) if isinstance(pos, str) else pos
        p = text_png(name, j, lines, style); extra += ["-loop", "1", "-i", p]
        fc.append(f"{cur}[{idx}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1 - 0.034:.3f})'[o{j}]"); cur = f"[o{j}]"; idx += 1
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    fc.append(f"[{idx}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={total - 0.5:.3f}:d=0.5,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    out = OUT + f"HoHoHound_Mama_{name}.mp4"
    ff(ins + extra + ["-ss", f"{a0:.3f}", "-i", U + SONG[key][0], "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M", "-r", "30",
       "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", out])
    return out, round(total, 2)

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    for n in sys.argv[1:] or R:
        out, tot = build(n, 0)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        REUSE = True; build(n, round(-14 - I, 1)); REUSE = False; print("OK", n, tot, "s", flush=True)
