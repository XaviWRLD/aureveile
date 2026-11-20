"""10 native-style static retargeting ads (1080x1350, 4:5 feed) from real myHeatedGloves footage frames."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FR = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/scratchpad/na/fr/"
OUT = "/home/user/aureveile/edits/native_ads/images/"
F = "/usr/share/fonts/opentype/inter/Inter-"
def f(w, s): return ImageFont.truetype(F + w + ".otf", s)
FE = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
W, H = 1080, 1350
BURG = (122, 30, 44); CREAM = (246, 239, 227); YEL = (255, 194, 58)

def is_emo(ch): return ord(ch) >= 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF or ch in "✅❌"
def text(im, xy, s, font, fill="white", stroke=0, sfill=(0, 0, 0), anchor="l", width=None):
    """Draw one line with inline color emoji. anchor l/c. Returns width."""
    d = ImageDraw.Draw(im); es = int(font.size * 1.05); parts = []
    for ch in s:
        if ch == "️": continue
        e = is_emo(ch)
        if parts and not e and not parts[-1][0]: parts[-1][1] += ch
        else: parts.append([e, ch])
    ws = [es + 6 if e else d.textlength(t, font=font) for e, t in parts]; tw = sum(ws)
    x, y = xy; x = x - tw / 2 if anchor == "c" else x
    for (e, t), w in zip(parts, ws):
        if e:
            g = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(g).text((0, 0), t, font=FE, embedded_color=True)
            g = g.crop(g.getbbox()).resize((es, es), Image.LANCZOS); im.alpha_composite(g, (int(x + 3), int(y + font.size * 0.08)))
        else:
            d.text((x, y), t, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
        x += w
    return tw

def photo(name, box=(W, H), focus=0.5):
    im = Image.open(FR + name + ".png").convert("RGBA"); bw, bh = box
    s = max(bw / im.width, bh / im.height); im = im.resize((int(im.width * s + .5), int(im.height * s + .5)), Image.LANCZOS)
    top = int((im.height - bh) * focus); left = (im.width - bw) // 2
    return im.crop((left, top, left + bw, top + bh))

def native_lines(im, lines, y, size=56, lh=1.25, fill="white"):
    ft = f("Bold", size)
    for i, l in enumerate(lines): text(im, (W / 2, y + i * size * lh), l, ft, fill, stroke=6, anchor="c")

def card(im, box, r=36, fill=(255, 255, 255, 245)):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([box[0], box[1] + 8, box[2], box[3] + 8], r, fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill)

def save(im, n, name): os.makedirs(OUT, exist_ok=True); im.convert("RGB").save(f"{OUT}{n:02d}_{name}.jpg", quality=93)

# 01 Notes-app list
im = photo("coffee_park", focus=0.55); card(im, (70, 120, 1010, 760), 40, (255, 253, 245, 250)); d = ImageDraw.Draw(im)
d.text((120, 160), "Notes", font=f("Bold", 40), fill=(225, 160, 20))
d.text((120, 225), "Things you can stop doing this winter:", font=f("Bold", 42), fill=(25, 25, 25))
for i, s in enumerate(["❌ Hands in your armpits at the bus stop", "❌ Hand warmers that die in 20 min", "❌ Sitting on your hands in the car", "❌ Taking gloves off to warm up", "✅ One click → warm hands 🔥"]):
    text(im, (120, 305 + i * 86), s, f("Medium", 38), (40, 40, 40))
save(im, 1, "NotesApp_StopDoing")

# 02 Comment-reply
im = photo("press", focus=0.45); card(im, (90, 150, 990, 420), 40)
d = ImageDraw.Draw(im); d.text((140, 180), "Most asked question", font=f("Regular", 34), fill=(110, 110, 110))
text(im, (140, 235), "Do they actually get warm? 🤔", f("Bold", 50), (20, 20, 20))
d.text((140, 320), "↳ Yes. Press the button, pick 1 of 3 levels.", font=f("Medium", 36), fill=(60, 60, 60))
native_lines(im, ["That first warm moment", "on a freezing morning 🔥"], 1150, 52)
save(im, 2, "CommentReply_DoTheyGetWarm")

# 03 Regular gloves vs heated gloves
im = Image.new("RGBA", (W, H), CREAM); ph = photo("holdboth", (W, 760), 0.4); im.alpha_composite(ph, (0, 590)); d = ImageDraw.Draw(im)
d.text((W / 2, 70), "Regular gloves vs. heated gloves", font=f("Black", 54), fill=(20, 20, 20), anchor="mt")
rows = [("Warm when you start walking", "Warm with one click"), ("Fingers numb after 15 min", "3 heat levels"), ("Hand warmers you rebuy", "Runs on AA batteries")]
d.text((270, 170), "Regular", font=f("Bold", 40), fill=(130, 130, 130), anchor="mt"); d.text((810, 170), "Heated", font=f("Bold", 40), fill=BURG, anchor="mt")
for i, (a, b) in enumerate(rows):
    y = 240 + i * 105; d.rounded_rectangle((40, y, 530, y + 88), 22, fill=(255, 255, 255)); d.rounded_rectangle((550, y, 1040, y + 88), 22, fill=(255, 255, 255))
    text(im, (60, y + 22), "❌ " + a, f("Medium", 31), (90, 90, 90)); text(im, (570, y + 22), "✅ " + b, f("Bold", 31), (25, 25, 25))
save(im, 3, "Comparison_RegularVsHeated")

# 04 Always-cold gift (native text)
im = photo("snowwalk", focus=0.5); native_lines(im, ["Buy these for the person", "who's ALWAYS cold 🥶"], 150, 64)
native_lines(im, ["(they'll steal yours otherwise) 😂"], 330, 44)
native_lines(im, ["Give them warm hands all winter 🎁"], 1180, 52)
save(im, 4, "Gift_AlwaysCold")

# 05 Raynaud's / always-cold fingers text-post
im = Image.new("RGBA", (W, H), (255, 255, 255)); im.alpha_composite(photo("led3", (W, 820), 0.45), (0, 530)); d = ImageDraw.Draw(im)
for i, l in enumerate(["If your fingers go white and numb", "every time it's cold out…", "", "this is the one gadget worth having 🧤🔥"]):
    text(im, (60, 70 + i * 72), l, f("Bold" if i < 2 else "Medium", 48), (15, 15, 15))
d.text((60, 400), "3 heat levels · one button · AA batteries", font=f("Regular", 36), fill=(90, 90, 90))
d.text((60, 455), "A comfort product, not a medical treatment.", font=f("Regular", 26), fill=(150, 150, 150))
save(im, 5, "TextPost_AlwaysColdFingers")

# 06 No charging
im = photo("strap", focus=0.5); native_lines(im, ["No charging. No cables.", "No “oops it's dead”. 🔋"], 140, 64)
card(im, (150, 1040, 930, 1250), 36, (0, 0, 0, 165))
text(im, (W / 2, 1068), "3× AA per glove", f("Black", 58), YEL, anchor="c"); text(im, (W / 2, 1160), "swap & go, anywhere", f("Bold", 44), "white", anchor="c")
save(im, 6, "Battery_NoCharging")

# 07 Bundle math
im = photo("coffee_park", focus=0.5); native_lines(im, ["Remember when you", "actually liked winter? ❄️"], 140, 66)
native_lines(im, ["Long walks. Hot coffee. Warm hands. 🔥"], 1180, 46)
save(im, 7, "Desire_LikeWinterAgain")

# 08 Dog walker
im = photo("snowwalk", focus=0.35); native_lines(im, ["6am dog walk.", "20°F. Hands: warm. 🐕🔥"], 150, 66)
native_lines(im, ["Heated gloves · 3 heat levels"], 1180, 50)
save(im, 8, "DogWalker_6am")

# 09 Dad gift
im = photo("door", focus=0.4); native_lines(im, ["Dad: “I don't need", "anything for Christmas.”"], 140, 62)
native_lines(im, ["Also Dad, scraping the car at 7am: 🥶"], 340, 44)
native_lines(im, ["Heated gloves. He'll use them daily. 🎁"], 1180, 46)
save(im, 9, "DadGift")

# 10 How it works callout
im = photo("led3", focus=0.45); d = ImageDraw.Draw(im)
native_lines(im, ["How they work 👇"], 130, 66)
for y, s in [(560, "① Press the button"), (690, "② Pick 1 of 3 heat levels"), (820, "③ Warm hands 🔥")]:
    card(im, (470, y, 1040, y + 100), 26, (255, 255, 255, 240)); text(im, (500, y + 27), s, f("Bold", 37), (20, 20, 20))
native_lines(im, ["Warm hands in one click 🔥"], 1180, 54)
save(im, 10, "HowItWorks_3Steps")
print("done")
