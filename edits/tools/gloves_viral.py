"""20 myHeatedGloves Facebook Reels from clips we already have (no new generation).
Engagement-farming / debate hooks on frame 0 (from the Reels Scout: callouts, skits, Vs., reveal, ranking),
unboxing intro on several, product close-up, use case, payoff, CTA „Comment WARM“. Reuses the xmas_mums engine.
python3 gloves_viral.py [V01 V02 ...]"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import xmas_mums as X

E = "/home/user/aureveile/edits/"; U = X.U
S = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/hf/gen/"
X.C = {"unbox": S + "unbox.mp4", "unboxk": S + "unbox_kitchen.mp4", "sc2": S + "scene2.mp4", "sc3": S + "scene3.mp4",
       "gcar": E + "scout_reels/clips/g_car.mp4", "g1s": E + "scout_reels/clips/g1_seedance.mp4",
       "wa1": U + "bed81630-VID-20261112-WA0001.mp4", "wa0": U + "b20696f0-VID-20261112-WA0000.mp4", "wa2": U + "3727053c-VID-20261112-WA0002.mp4"}
X.C.update({f"G{i}": E + f"niche_reels/clips/G{i}.mp4" for i in range(1, 8)})
X.SONG = {"bmb": ("d078ba83-Be_My_Baby.mp3", 4.2), "mambo": ("d4eec954-Mambo_No_5.mp3", 6.83),
          "lc": ("09c4c148-Last_Christmas.mp3", 7.709), "lcp": ("fc628e28-Last_Christmas_-_Pudding_Mix.mp3", None),
          "sr": ("e73f2714-Sleigh_Ride.mp3", 4.11), "sr1": ("b52e4c65-Sleigh_Ride_1.mp3", None),
          "aiw": ("9d88af6e-All_I_Want_for_Christmas_Is_You.mp3", 49.76), "cb": ("115c4178-Christmas_Baby_Please_Come_Home.mp3", 12.12),
          "swm": ("d40c44b9-Somebodys_Watching_Me.mp3", None), "hw": ("27fc37e0-Housewife.mp3", 37.198),
          "fl": ("6b8aec8a-Faded_love.mp3", None), "ts": ("b3e609da-Training_Season_Live_from_the_Royal_Albert_Hall.mp3", None)}
X.BC = X.TMP + "beats_gloves.json"
X.OUT = E + "gloves_viral/"
X.CTA = ["Comment WARM for the link 👇"]

# (clip, src_start, dur, opts)  dur = beats if beat else seconds · text (lines, pos, from_seg, to_seg|None, style)
X.R = {
 "V01": dict(song="mambo", beat=True, punch=True, segs=[("g1s", 2.65, 3, {"sp": 0.6}), ("unbox", 0.8, 3, {}), ("wa1", 8.0, 3, {}), ("sc3", 0.5, 5, {})],
    text=[(["Unpopular opinion:", "normal gloves are a scam 🧤"], "top", 0, None, "b"),
          (["Fight me in the comments 👇"], 1250, 3, None, "s")]),
 "V02": dict(song="hw", beat=True, punch=True, segs=[("unboxk", 0.3, 4, {}), ("G1", 4.9, 4, {}), ("G1", 6.83, 3, {}), ("G1", 8.42, 3, {"sp": 0.8})],
    text=[(["My husband said these were", "a waste of money…"], "top", 0, 1, "b"),
          (["He hasn't taken them off since 🙄"], "top", 2, None, "b"),
          (["Waste of money or best gift? 👇"], 1250, 3, None, "s")]),
 "V03": dict(song="fl", beat=False, punch=False, grade="warm", segs=[("unbox", 0.0, 4.2, {"sp": 0.8}), ("wa0", 4.2, 2.2, {}), ("wa1", 8.0, 2.4, {"sp": 0.7}), ("wa2", 13.6, 1.6, {})],
    text=[(["Rate this unboxing 1–10 👇"], "top", 0, None, "b"), (["Be honest 😅"], 1250, 3, None, "s")]),
 "V04": dict(song="bmb", beat=False, punch=True, segs=[("G2", 0.0, 2.4, {}), ("G2", 2.4, 2.1, {}), ("G2", 4.54, 1.5, {}), ("G2", 6.04, 1.4, {}), ("G2", 7.5, 2.5, {})],
    text=[(["Men will buy a new grill every summer", "but won't spend a cent on warm hands 🙄"], "top", 0, 1, "b"),
          (["…until the boys try them 😂"], "top", 2, None, "b"), (["Tag a man who needs this 👇"], 1250, 4, None, "s")]),
 "V05": dict(song="lc", beat=True, punch=True, segs=[("G5", 0.0, 2, {}), ("G5", 1.3, 4, {}), ("G5", 5.38, 2, {}), ("G5", 8.5, 4, {"sp": 0.8})],
    text=[(["Tell me you're always cold", "without telling me 🥶"], "top", 0, None, "b"),
          (["Wrong answers only 👇"], 1250, 3, None, "s")]),
 "V06": dict(song="sr", beat=True, punch=True, segs=[("sc3", 0.0, 3, {}), ("gcar", 0.3, 3, {}), ("wa2", 6.0, 3, {}), ("wa2", 10.0, 3, {}), ("sc3", 2.5, 3, {})],
    text=[(["Is this cheating at winter? 🤔"], "top", 0, None, "b"), (["Yes or no 👇"], 1250, 4, None, "s")]),
 "V07": dict(song="swm", beat=False, punch=True, flash=True, segs=[("wa0", 2.2, 2.6, {"freeze": 1.2}), ("wa1", 8.0, 2.2, {}), ("wa2", 14.0, 1.0, {}), ("sc3", 0.5, 3.6, {})],
    text=[(["Wrong answers only:", "what does this red button do? 👇"], "top", 0, 0, "b"),
          (["3 bars of heat in one click 🔥"], "top", 1, None, "b")]),
 "V08": dict(song="hw", beat=False, punch=True, segs=[("g1s", 8.0, 2.0, {"freeze": 1.2}), ("g1s", 10.0, 2.0, {}), ("g1s", 6.0, 2.0, {}), ("g1s", 4.0, 2.0, {}), ("g1s", 10.0, 2.0, {})],
    text=[(["Him: „I'm not cold.“"], "top", 0, 0, "b"), (["Also him:"], "top", 1, 1, "b"),
          (["Me:"], "top", 2, 3, "b"), (["Why are men like this? 😂👇"], "top", 4, None, "b")]),
 "V09": dict(song="bmb", beat=True, punch=True, segs=[("sc2", 0.2, 4, {}), ("wa0", 2.2, 3, {}), ("gcar", 0.3, 4, {}), ("sc3", 1.0, 4, {})],
    text=[(["Rich people don't have cold hands.", "Change my mind 🤷"], "top", 0, None, "b")]),
 "V10": dict(song="mambo", beat=True, punch=True, segs=[("G4", 0.0, 3, {}), ("G2", 0.0, 3, {}), ("wa1", 8.0, 3, {}), ("wa2", 6.0, 4, {})],
    text=[(["Normal gloves vs. hand warmers", "vs. THESE – pick one 👇"], "top", 0, None, "b"),
          (["1. Normal gloves 🥶"], 1250, 0, 0, "s"), (["2. Hand warmers 😐"], 1250, 1, 1, "s"), (["3. These 🔥"], 1250, 2, None, "s")]),
 "V11": dict(song="ts", beat=False, punch=True, segs=[("G3", 0.0, 2.5, {}), ("G3", 2.46, 1.2, {}), ("G3", 3.67, 2.2, {}), ("G3", 5.88, 2.0, {}), ("G3", 7.88, 2.1, {})],
    text=[(["Sorry, but if your hands are still", "freezing in 2026, that's on you 😬"], "top", 0, None, "b"),
          (["Agree or disagree? 👇"], 1250, 4, None, "s")]),
 "V12": dict(song="aiw", beat=True, punch=True, segs=[("unboxk", 0.2, 2, {}), ("sc2", 0.5, 2, {}), ("unbox", 2.5, 2, {}), ("wa1", 8.0, 2, {}), ("G1", 8.42, 4, {"sp": 0.8})],
    text=[(["POV: the gift nobody expected", "to be everyone's favourite 🎁"], "top", 0, None, "b")]),
 "V13": dict(song="sr1", beat=False, punch=True, segs=[("wa1", 8.0, 1.6, {}), ("wa0", 2.4, 1.4, {}), ("G5", 5.38, 1.2, {}), ("G2", 4.6, 1.4, {}), ("wa2", 14.0, 1.0, {}), ("G1", 6.9, 1.5, {}), ("sc3", 0.5, 2.4, {})],
    text=[(["The most satisfying click", "of winter 🔊"], "top", 0, None, "b"), (["Sound on 🔥"], 1250, 0, 1, "s")]),
 "V14": dict(song="lcp", beat=True, punch=True, segs=[("unbox", 0.3, 4, {}), ("wa0", 2.2, 3, {}), ("sc3", 0.3, 5, {})],
    text=[(["Do NOT buy these if you", "enjoy having cold hands 🙃"], "top", 0, None, "b")]),
 "V15": dict(song="fl", beat=False, punch=False, segs=[("g1s", 2.65, 2.2, {"sp": 0.5}), ("G5", 0.0, 1.2, {}), ("G4", 0.0, 1.75, {}), ("wa2", 6.0, 3.0, {}), ("sc3", 0.5, 2.4, {})],
    text=[(["Things I'll never go back to", "after these 🧤"], "top", 0, None, "b"),
          (["Blowing on my hands 🌬️"], 1250, 0, 0, "s"), (["Sitting on my hands 🥶"], 1250, 1, 1, "s"),
          (["Numb fingers at 7am 😩"], 1250, 2, 2, "s"), (["Now: warm in one click 🔥"], 1250, 3, None, "s")]),
 "V16": dict(song="bmb", beat=False, punch=True, segs=[("unboxk", 0.0, 4.2, {}), ("unboxk", 4.2, 1.6, {"freeze": 0.6}), ("wa1", 8.0, 2.0, {}), ("sc2", 3.0, 2.0, {})],
    text=[(["Wait for her reaction 😳"], "top", 0, 0, "b"), (["That's the face 😂"], "top", 1, None, "b")]),
 "V17": dict(song="aiw", beat=False, punch=False, segs=[("G1", 8.42, 9.0, {"sp": 0.17, "split": ("G5", 8.5), "top_sp": 0.17})],
    text=[(["Who wore it better? 1 or 2 👇"], 820, 0, None, "b")], numbers2=True),
 "V18": dict(song="mambo", beat=False, punch=False, segs=[("g1s", 2.65, 9.5, {"sp": 0.12, "split": ("wa2", 6.0), "top_sp": 0.2})],
    text=[(["Without 🥶"], 120, 0, None, "b"), (["With 🔥"], 1060, 0, None, "b")]),
 "V19": dict(song="hw", beat=False, punch=True, segs=[("G6", 0.0, 1.1, {"freeze": 0.9}), ("G6", 1.04, 3.4, {}), ("G6", 4.54, 3.0, {}), ("G6", 8.88, 1.16, {})],
    text=[(["My dad says heated gloves", "are for „soft“ people 🙄"], "top", 0, 1, "b"),
          (["Dad, 10 minutes later:"], "top", 2, None, "b"), (["Who's right? 👇"], 1250, 3, None, "s")]),
 "V20": dict(song="sr", beat=True, punch=True, segs=[("unbox", 0.5, 5, {}), ("wa1", 8.0, 3, {}), ("G3", 3.7, 4, {}), ("G2", 7.5, 3, {})],
    text=[(["Day 1 vs. day 30 of owning", "heated gloves"], "top", 0, None, "b"),
          (["Day 1: excited 🎁"], 1250, 0, 1, "s"), (["Day 30: still obsessed 🔥"], 1250, 2, None, "s")]),
}

# small engine additions: 1/2 labels for top/bottom split, output names
_orig_build = X.build
def build(name, gain):
    cfg = X.R[name]
    if cfg.get("numbers2") and not cfg.get("_n"):
        cfg["text"] = cfg["text"] + [(["1"], -10, 0, None, "big"), (["2"], 950, 0, None, "big")]; cfg["_n"] = True
    if cfg["beat"] and not cfg.get("_s"):   # fast songs: stretch beat counts so every Reel lands at ~9-13 s
        import numpy as np, math
        b, a = X.beats_of(cfg["song"]); i = int(np.argmin(abs(b - a))); per = float(np.median(np.diff(b[i:i + 16])))
        tot_b = sum(sg[2] for sg in cfg["segs"]); k = max(1, math.ceil(9.0 / (tot_b * per)))
        cfg["segs"] = [(c, st, d * k, o) for c, st, d, o in cfg["segs"]]; cfg["_s"] = True
    out, tot = _orig_build(name, gain)
    new = X.OUT + f"Gloves_Viral_{name}.mp4"; os.replace(out, new); return new, tot
X.build = build

if __name__ == "__main__":
    os.makedirs(X.TMP, exist_ok=True); os.makedirs(X.OUT, exist_ok=True)
    for n in sys.argv[1:] or X.R:
        X.REUSE = False; out, tot = build(n, 0)
        I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-i", out, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
        X.REUSE = True; build(n, round(-14 - I, 1)); X.REUSE = False; print("OK", n, tot, "s", flush=True)
