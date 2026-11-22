"""Finish the 14 niche-callout Seedance clips (22 Nov) into Reels.
Hook (niche callout) on top for the whole clip, optional per-shot labels, CTA bottom on the last ~2.6 s,
song started on a beat inside its loudest 12 s, zoom punch on each detected cut, two-pass -14 LUFS.
python3 niche_reels.py [G1 H3 ...]"""
import subprocess, sys, os, re, json
import numpy as np, librosa
sys.path.insert(0, os.path.dirname(__file__))
from hohohound_9 import render

U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
CL = "/home/user/aureveile/edits/niche_reels/clips/"
OUT = "/home/user/aureveile/edits/niche_reels/"
TMP = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/niche_ov/"
SC = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
GC = ["Comment WARM for the link 👇"]
SANTA = ["Schreib „SANTA“ für den Link 👇"]
BAUM = ["Schreib „BAUM“ für den Link 👇"]
R = {
 "G1": ("Be_My_Baby", ["If you warm your freezing hands", "on your husband's back…", "this one's for him 😂"], GC, None),
 "G2": ("Mambo_No_5", ["Duck hunters at 5am,", "this is for you 🦆"], GC, None),
 "G3": ("Training_Season_Live_from_the_Royal_Albert_Hall", ["Do NOT let a horse girl", "see this 🐴"], GC, None),
 "G4": ("Last_Christmas", ["Night shift nurses walking", "to the car at 7am 🥶"], GC, None),
 "G5": ("Christmas_Baby_Please_Come_Home", ["If you sit on your hands", "to warm them up… 🥶"], GC, None),
 "G6": ("Sleigh_Ride_1", ["If your dad REFUSES", "to wear gloves…"], GC, None),
 "G7": ("Somebodys_Watching_Me", ["Rating winter gear", "as a mail carrier 📬"], GC, ["Thermos: 6/10", "Hat: 5/10", "Hand warmers: 3/10", "Heated gloves: 11/10 🔥"]),
 "H1": ("All_I_Want_for_Christmas_Is_You", ["Erstes Weihnachten mit", "unserem Tierschutzhund 🥹"], BAUM, None),
 "H2": ("Sleigh_Ride", ["Dackel-Mamas,", "ihr werdet das lieben 🌭🎄"], BAUM, None),
 "H3": ("Mambo_No_5", ["Für alle, deren Hund mehr", "Geschenke kriegt als sie selbst 🎁"], SANTA, None),
 "H4": ("Last_Christmas_-_Pudding_Mix", ["Zwergspitz-Besitzer,", "das hier ist für euch 🧡"], BAUM, None),
 "H5": ("Sleigh_Ride_1", ["Frenchie-Eltern wissen:", "Er MUSS bei jedem Trend mitmachen 😂"], SANTA, None),
 "H6": ("Be_My_Baby", ["Für alle, deren Hund schneller", "Pakete aufmacht als sie selbst 📦"], BAUM, None),
 "H7": ("All_I_Want_for_Christmas_Is_You", ["Wenn dein Hund auf JEDEM", "Familienfoto drauf sein muss 📸"], BAUM, None),
}

def song_path(key):
    c = [f for f in os.listdir(U) if f.split("-", 1)[1] == key + ".mp3"]
    return U + sorted(c)[0]

def song_start(path, dur):
    y, sr = librosa.load(path, sr=22050, mono=True)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]; t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
    win = int(dur * sr / 512); cs = np.convolve(rms, np.ones(win), "valid")
    lim = t < (len(y) / sr - dur - 1); i = int(np.argmax(np.where(lim[:len(cs)], cs, 0)))
    _, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    b = beats[np.argmin(abs(beats - t[i]))] if len(beats) else t[i]
    return float(b)

def cuts_of(f):
    e = subprocess.run(["ffmpeg", "-i", f, "-vf", "select='gt(scene,0.28)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    out = []
    for x in [float(v) for v in re.findall(r"pts_time:([\d.]+)", e)]:
        if x > 0.8 and (not out or x - out[-1] > 1.0): out.append(x)
    return out

def build(name, gain, a0):
    song, hook, cta, seq = R[name]; src = CL + name + ".mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    total = dur - 0.05; cuts = cuts_of(src)
    zs = "+".join(f"0.05*max(0\\,1-(t-{x:.3f})/0.18)*gte(t\\,{x:.3f})" for x in cuts) or "0"
    fc = [f"[0:v]fps=30,{SC},scale=w='trunc(1080*(1+{zs})/2)*2':h='trunc(1920*(1+{zs})/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,eq=contrast=1.03:saturation=1.04,unsharp=5:5:0.4[v0]"]
    cta_t = total - 2.6
    ov = [(render(hook, TMP + f"{name}_h.png"), 200, 0, total + 1), (render(cta, TMP + f"{name}_c.png"), 1460, cta_t, total + 1)]
    if seq:
        bounds = [0.0] + cuts[:len(seq) - 1] + [total + 1]
        if len(bounds) < len(seq) + 1:  # not enough cuts: split evenly
            bounds = list(np.linspace(0, total, len(seq) + 1)); bounds[-1] = total + 1
        for k, s in enumerate(seq):
            ov.append((render([s], TMP + f"{name}_s{k}.png"), 1250, bounds[k] + 0.1, bounds[k + 1]))
    cur = "[v0]"; extra = []
    for j, (p, y, t0, t1) in enumerate(ov):
        extra += ["-loop", "1", "-i", p]
        fc.append(f"{cur}[{1+j}:v]overlay=x=0:y={y}+10*max(0\\,1-(t-{t0:.3f})/0.12):enable='between(t\\,{t0:.3f}\\,{t1-0.034:.3f})'[o{j}]"); cur = f"[o{j}]"
    fc.append(f"{cur}trim=0:{total:.3f},format=yuv420p[v]")
    fc.append(f"[{1+len(ov)}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={total-0.5:.3f}:d=0.5,volume={gain}dB,alimiter=limit=0.84:level=false[a]")
    out = OUT + f"{'Gloves' if name[0]=='G' else 'HoHoHound'}_{name}_Niche.mp4"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src] + extra + ["-ss", f"{a0:.3f}", "-i", song_path(song), "-filter_complex", ";".join(fc),
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "17", "-maxrate", "10M", "-bufsize", "20M",
        "-r", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", out], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
    return out, cuts

if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    for n in sys.argv[1:] or R:
        if not os.path.exists(CL + n + ".mp4"): print("skip", n); continue
        a0 = song_start(song_path(R[n][0]), 12)
        out, cuts = build(n, 0, a0)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        build(n, round(-14 - I, 1), a0); print("OK", n, round(a0, 2), [round(c, 2) for c in cuts])
