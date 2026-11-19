import os, re, subprocess, sys, time
import numpy as np, soundfile as sf

REF_SRC="voice-reference.mp3"; REF_WAV="ref.wav"; OUT="output.mp3"
MAX_CHARS=110; GAP_MS=140
SCRIPT = sys.argv[1] if len(sys.argv)>1 else "script.txt"

def split_script(path):
    t=open(path,encoding="utf-8").read().strip()
    parts=[s.strip() for s in re.split(r'(?<=[।.!?])\s+', t) if s.strip()]
    chunks=[]; buf=""
    for p in parts:
        if len(buf)+len(p)<=MAX_CHARS: buf=(buf+" "+p).strip()
        else:
            if buf: chunks.append(buf)
            buf = p if len(p)<=MAX_CHARS else p[:MAX_CHARS]
    if buf: chunks.append(buf)
    return chunks

subprocess.run(["ffmpeg","-y","-v","error","-ss","0.15","-t","7.4","-i",REF_SRC,
                "-ar","24000","-ac","1","-c:a","pcm_s16le",REF_WAV], check=True)
ref_text=open("ref_text.txt",encoding="utf-8").read().strip()
print("script:", SCRIPT, flush=True)
chunks=split_script(SCRIPT); print("chunks:", len(chunks), flush=True)

t0=time.time()
from huggingface_hub import hf_hub_download
vocab = hf_hub_download("ai4bharat/IndicF5", "checkpoints/vocab.txt")
print("vocab:", vocab, flush=True)
try:
    ckpt = hf_hub_download("Saravananravi/indicf5-hinglish", "model.safetensors")
    print("USING hinglish model:", ckpt, os.path.getsize(ckpt), flush=True)
except Exception as e:
    print("hinglish fetch failed:", str(e)[:200], flush=True)
    ckpt = hf_hub_download("ai4bharat/IndicF5", "model.safetensors")
    print("fallback to IndicF5:", ckpt, flush=True)

import torch, soundfile
from f5_tts.model import DiT
from f5_tts.infer.utils_infer import load_model, load_vocoder, infer_process

cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)
print("loading model (kwargs, no positional)", flush=True)
model = load_model(DiT, cfg, ckpt, mel_spec_type="vocos", vocab_file=vocab,
                   ode_method="euler", use_ema=True)
print("model loaded in", round(time.time()-t0,1),"s", flush=True)
vocoder = load_vocoder(vocoder_name="vocos", is_local=False, local_path=None, device="cpu")
print("vocoder loaded", flush=True)

SR=24000; pieces=[]
for i,c in enumerate(chunks,1):
    t1=time.time()
    wav, sr, spec = infer_process(REF_WAV, ref_text, c, model, vocoder,
                                  mel_spec_type="vocos", device="cpu", show_info=print)
    a=np.array(wav, dtype=np.float32).squeeze()
    if sr!=SR:
        sf.write("tmp.wav", a, sr)
        subprocess.run(["ffmpeg","-y","-v","error","-i","tmp.wav","-ar",str(SR),"-ac","1","tmp2.wav"], check=False)
        a,sr=sf.read("tmp2.wav", dtype="float32")
    dur=len(a)/SR
    print(f"  chunk {i}: {dur:.1f}s in {round(time.time()-t1,1)}s", flush=True)
    pieces.append(a.astype(np.float32)); pieces.append(np.zeros(int(SR*GAP_MS/1000),dtype=np.float32))

audio=np.concatenate(pieces) if pieces else np.zeros(SR,dtype=np.float32)
print("raw total:", round(len(audio)/SR,2),"s", flush=True)
sf.write("raw.wav", audio, SR)
subprocess.run(["ffmpeg","-y","-v","error","-i","raw.wav","-af",
  "silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB,highpass=f=70,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11",
  "-ar","24000","-ac","1","-b:a","96k",OUT], check=False)
print("SAVED", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else 0, flush=True)
