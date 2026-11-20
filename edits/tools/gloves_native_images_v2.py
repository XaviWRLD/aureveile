"""12 desire-led native static ads (1080x1350) from 4K Nano Banana scenes of the real myHeatedGloves product.
Two native text styles: TikTok outline text, and Instagram-story caption boxes."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from gloves_native_images import text, f

RAW = "/home/user/aureveile/edits/native_ads/v2_raw/"
OUT = "/home/user/aureveile/edits/native_ads/images_v2/"
W, H = 1080, 1350

def base(n):
    im = Image.open(f"{RAW}g{n:02d}.png").convert("RGB").resize((W, H), Image.LANCZOS)
    return im.convert("RGBA")

def outline(im, lines, y, size=58, lh=1.22):
    ft = f("Bold", size)
    for i, l in enumerate(lines): text(im, (W / 2, y + i * size * lh), l, ft, "white", stroke=6, anchor="c")

def boxes(im, lines, y, size=50, fg=(0, 0, 0), bg=(255, 255, 255, 240), pad=18):
    """Instagram-story style: each line in its own rounded white box."""
    ft = f("Bold", size); d = ImageDraw.Draw(im); lh = int(size * 1.42)
    for i, l in enumerate(lines):
        tw = text(Image.new("RGBA", (10, 10)), (0, 0), l, ft)  # measure
        x0 = (W - tw) / 2 - pad; yy = y + i * (lh + 4)
        d.rounded_rectangle([x0, yy, x0 + tw + 2 * pad, yy + lh], 16, fill=bg)
        text(im, (W / 2, yy + (lh - size * 1.18) / 2), l, ft, fg, anchor="c")

def save(im, n, name):
    os.makedirs(OUT, exist_ok=True); im.convert("RGB").save(f"{OUT}{n:02d}_{name}.jpg", quality=94)

im = base(1); boxes(im, ["the only one at the bus stop", "not suffering 😌"], 110); save(im, 1, "BusStop_NotSuffering")

im = base(2); outline(im, ["shake, wait, hope… vs. one click 🔥"], 90, 58)
d = ImageDraw.Draw(im)
for x, l in [(W * 0.25, "hand warmer 🥶"), (W * 0.75, "heated gloves 🔥")]:
    ft = f("Bold", 40); tw = text(Image.new("RGBA", (10, 10)), (0, 0), l, ft)
    d.rounded_rectangle([x - tw / 2 - 16, 1190, x + tw / 2 + 16, 1252], 14, fill=(255, 255, 255, 240))
    text(im, (x, 1196), l, ft, (0, 0, 0), anchor="c")
save(im, 2, "Split_HandWarmerVsGloves")

im = base(3); outline(im, ["6am walk. Freezing.", "Not even mad. 🐕"], 110, 66); save(im, 3, "DogWalk_NotEvenMad")

im = base(4); boxes(im, ["Dad finally stopped complaining", "about the frozen car 😂"], 90, 46); save(im, 4, "Dad_FrozenCar")

im = base(5); boxes(im, ["the gift she'll use", "every single cold day 🎁"], 1080, 50); save(im, 5, "Gift_EveryColdDay")

im = base(6); outline(im, ["me, the always-cold one,", "finally winning ☕️"], 1110, 56); save(im, 6, "AlwaysCold_FinallyWinning")

im = base(7); d = ImageDraw.Draw(im)
sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([90, 118, 990, 668], 40, fill=(0, 0, 0, 90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
d.rounded_rectangle([90, 110, 990, 660], 40, fill=(255, 253, 245, 250))
d.text((140, 145), "Notes", font=f("Bold", 38), fill=(225, 160, 20))
d.text((140, 205), "Things I'm not doing this winter:", font=f("Bold", 42), fill=(25, 25, 25))
for i, s in enumerate(["❌ sitting on my hands in the car", "❌ hand warmers that die by 9am", "❌ rushing home from every walk", "✅ one click → warm hands 🔥"]):
    text(im, (140, 290 + i * 88), s, f("Medium", 38), (40, 40, 40))
save(im, 7, "NotesApp_NotDoing")

im = base(8); outline(im, ["Regular gloves keep heat in.", "These make it. 🔥"], 120, 60)
d = ImageDraw.Draw(im)
for x, l in [(W * 0.36, "heated"), (W * 0.8, "regular")]:
    ft = f("Bold", 40); tw = d.textlength(l, font=ft)
    d.rounded_rectangle([x - tw / 2 - 16, 1220, x + tw / 2 + 16, 1282], 14, fill=(255, 255, 255, 235)); d.text((x, 1228), l, font=ft, fill=(0, 0, 0), anchor="mt")
save(im, 8, "UsVsThem_KeepVsMake")

im = base(9); boxes(im, ["Saturday 8am sideline.", "Hands: fine. ⚽️"], 100, 52); save(im, 9, "Sideline_HandsFine")

im = base(10); outline(im, ["no charging.", "just AAs in my bag 🔋"], 1100, 62); save(im, 10, "Bag_NoCharging")

im = base(11); outline(im, ["didn't take them off once 📱"], 110, 60)
boxes(im, ["touchscreen fingertips"], 1210, 40); save(im, 11, "Touchscreen_NeverOff")

im = base(12); outline(im, ["soaked in snow.", "still warm. ❄️🔥"], 1090, 64)
boxes(im, ["waterproof"], 90, 40); save(im, 12, "Waterproof_SnowballFight")
print("done")
