import os, re, subprocess, time
import numpy as np

REF = "voice-reference.mp3"
OUT = "output.mp3"
MAX_CHARS = 120          # keep each generation short: long inputs make chatterbox loop
GAP_MS = 160

def split_script(path):
    t = open(path, encoding="utf-8").read().strip()
    parts = [s.strip() for s in re.split(r'(?<=[।.!?])\s+', t) if s.strip()]
    chunks = []
    for p in parts:
        if len(p) <= MAX_CHARS:
            chunks.append(p)
        else:
            buf = ""
            for piece in re.split(r'(?<=[,;])\s+', p):
                if len(buf) + len(piece) <= MAX_CHARS:
                    buf = (buf + " " + piece).strip()
                else:
                    if buf: chunks.append(buf)
                    buf = piece
            if buf: chunks.append(buf)
    return chunks

# trim reference to ~18s
subprocess.run(["ffmpeg","-y","-v","error","-i",REF,"-t","18","-ac","1","-ar","24000","ref.wav"], check=False)
ref = "ref.wav" if os.path.exists("ref.wav") else REF

chunks = split_script("script.txt")
print("chunks:", len(chunks))
for i,c in enumerate(chunks,1): print(f"  {i}. [{len(c)}] {c[:70]}")

t0 = time.time()
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
sr = m.sr
print("model ready in", round(time.time()-t0,1), "s, sr =", sr)

pieces = []
for i, c in enumerate(chunks, 1):
    t1 = time.time()
    wav = m.generate(c, language_id="hi", audio_prompt_path=ref)
    a = wav.squeeze().cpu().numpy()
    dur = len(a)/sr
    # loop guard: a 120-char chunk should never take more than ~12s
    if dur > 14:
        print(f"  chunk {i}: {dur:.1f}s looks like a loop, retrying once")
        wav = m.generate(c, language_id="hi", audio_prompt_path=ref)
        a = wav.squeeze().cpu().numpy(); dur = len(a)/sr
    print(f"  chunk {i}: {dur:.1f}s in {round(time.time()-t1,1)}s")
    pieces.append(a)
    pieces.append(np.zeros(int(sr*GAP_MS/1000), dtype=np.float32))

audio = np.concatenate(pieces) if pieces else np.zeros(sr, dtype=np.float32)
print("total audio:", round(len(audio)/sr,2), "s")

import torch, torchaudio
torchaudio.save(OUT, torch.from_numpy(audio).unsqueeze(0), sr)
print("SAVED", OUT, round(len(audio)/sr,2), "s | total", round(time.time()-t0,1), "s")
