import subprocess, sys, os
U = "/root/.claude/uploads/36f44319-1f84-532a-991c-8803b39245c5/"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; Y = "0xFFC23A"; SP = 1.1
SONG = {"lx": ("09c4c148-Last_Christmas.mp3", 7.709), "hw": ("27fc37e0-Housewife.mp3", 37.198),
        "mc": ("9d88af6e-All_I_Want_for_Christmas_Is_You.mp3", 49.760)}
V = [
 ("01_Raynauds", "4a74c44c-myHeatedGloves_01_Raynauds_1080p.mp4", "lx", [2.833,5.958,9.042,11.917,13.833,16.375,20.042], 5.958,
  [("FINGERS GO WHITE", "white"), ("IN THE COLD?", "white"), ("THIS IS FOR YOU", Y)]),
 ("02_Cold_Hands_Friend", "ed32eac0-myHeatedGloves_02_Cold_Hands_Friend_1080p.mp4", "hw", [1.458,3.125,6.375,8.583,10.292,12.083,15.667,19.583], 6.375,
  [("TAG YOUR", "white"), ("ALWAYS-COLD FRIEND", "white"), ("YOU KNOW WHO", Y)]),
 ("03_Winter_Gift", "07c3130e-myHeatedGloves_03_Winter_Gift_1080p.mp4", "mc", [2.833,6.0,8.875,12.042,13.625,15.667,19.75], 6.0,
  [("STOP GIFTING", "white"), ("CANDLES.", "white"), ("GIVE THIS INSTEAD", Y)]),
]
END = 23.1
def esc(s): return s.replace("'", "’").replace(":", "\\:").replace(",", "\\,")
for name, src, song, cuts, reveal, hook in V:
    L = END / SP; cs = [c / SP for c in cuts]; rv = reveal / SP; he = 2.6 / SP
    zs = "+".join(f"0.07*max(0\\,1-(t-{c:.3f})/0.2)*gte(t\\,{c:.3f})" for c in cs)
    Z = f"(1+0.05*max(0\\,1-t/0.35)+{zs})"
    dt = []
    for i, (txt, col) in enumerate(hook):
        fs = min(96, int(960 / (0.62 * len(txt))))
        dt.append(f"drawtext=fontfile={FONT}:text='{esc(txt)}':fontsize={fs}:fontcolor={col}:borderw=9:bordercolor=black@0.95:"
                  f"shadowx=0:shadowy=6:shadowcolor=black@0.5:x=(w-text_w)/2:y={250 + i*108}+20*max(0\\,1-t/0.15):enable='lt(t\\,{he:.3f})'")
    sf, hit = SONG[song]; ss = hit - rv
    fc = (f"[0:v]trim=0:{END},setpts=(PTS-STARTPTS)/{SP},fps=30,"
          f"scale=w='trunc(1080*{Z}/2)*2':h='trunc(1920*{Z}/2)*2':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,"
          f"eq=contrast=1.04:saturation=1.08[zv];"
          f"color=white:s=1080x1920:r=30:d={L:.3f},format=rgba,geq=r=255:g=255:b=255:a='255*0.6*max(0\\,1-(T-{rv:.3f})/0.15)*gte(T\\,{rv:.3f})'[fl];"
          f"[zv][fl]overlay=0:0:shortest=1," + ",".join(dt) + ",format=yuv420p[v];"
          f"[0:a]atrim=0:{END},asetpts=PTS-STARTPTS,atempo={SP},highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume=1.4,asplit[vo][key];"
          f"[1:a]atrim=0:{L+0.5:.3f},asetpts=PTS-STARTPTS,volume=0.22,afade=t=in:d=0.3,afade=t=out:st={L-0.8:.3f}:d=0.8[m];"
          f"[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
          f"[vo][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", U + src, "-ss", f"{ss:.3f}", "-i", U + sf, "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "256k", "-ar", "44100", "-t", f"{L:.3f}", f"{OUT}/myHeatedGloves_{name}_VIRAL.mp4"], capture_output=True, text=True)
    print(name, f"{L:.1f}s", "OK" if r.returncode == 0 else r.stderr[-600:], flush=True)
