from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
S = "/tmp/claude-0/-home-user-aureveile/36f44319-1f84-532a-991c-8803b39245c5/"
OUT = "/home/user/aureveile/edits/thumbnails/"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
Y = (255, 194, 58); W = (255, 255, 255)
def cover(src, lines, band, name):
    im = Image.open(src).convert("RGB")
    r = max(1080 / im.width, 1920 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l = (im.width - 1080) // 2; t = (im.height - 1920) // 2
    im = im.crop((l, t, l + 1080, t + 1920))
    im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Color(im).enhance(1.08)
    # soft dark gradient behind the text band for legibility
    y0, y1 = band
    grad = Image.new("L", (1080, 1920), 0); g = ImageDraw.Draw(grad)
    for y in range(y0 - 120, y1 + 120):
        d = 1 - min(1, max(0, (y0 - y) / 120, (y - y1) / 120))
        g.line([(0, y), (1080, y)], fill=int(150 * d))
    im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im, grad.filter(ImageFilter.GaussianBlur(30)))
    dr = ImageDraw.Draw(im); y = y0
    for txt, size, col in lines:
        f = ImageFont.truetype(FONT, size)
        while dr.textlength(txt, font=f) > 980: size -= 4; f = ImageFont.truetype(FONT, size)
        w = dr.textlength(txt, font=f)
        dr.text(((1080 - w) / 2, y), txt, font=f, fill=col, stroke_width=max(6, size // 14), stroke_fill=(0, 0, 0))
        y += int(size * 1.12)
    im.save(OUT + name, quality=95)
    im.resize((360, 640)).save(S + "scratchpad/qa/" + name)
cover(S + "images/4.webp", [("COLD HANDS", 150, W), ("ALL WINTER?", 150, Y)], (270, 600), "Cover_V1_ColdHands.jpg")
cover(S + "scratchpad/hf/gen/kend.png", [("HUSBANDS,", 150, W), ("TAKE NOTES.", 150, Y)], (1270, 1600), "Cover_V2_Husbands.jpg")
cover(S + "scratchpad/hf/gen/end1.png", [("UNPOPULAR OPINION", 76, W), ("NORMAL GLOVES", 128, W), ("ARE USELESS?", 128, Y)], (290, 720), "Cover_V3_Unpopular.jpg")
print("ok")
