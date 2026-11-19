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

import torch, soundfile, inspect
from f5_tts.model import DiT
import f5_tts.infer.utils_infer as UI

print("utils_infer has:", [n for n in dir(UI) if 'load' in n or 'infer' in n], flush=True)
load_model = UI.load_model
load_vocoder = UI.load_vocoder
infer_process = UI.infer_process
print("load_model signature:", inspect.signature(load_model), flush=True)
print("infer_process signature:", inspect.signature(infer_process), flush=True)

cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)
params = inspect.signature(load_model).parameters
kw = {}
for k, v in dict(mel_spec_type="vocos", vocab_file=vocab, ode_method="euler", use_ema=True, device="cpu").items():
    if k in params: kw[k] = v
print("load_model kwargs:", list(kw), flush=True)
model = load_model(DiT, cfg, **kw)
print("model built in", round(time.time()-t0,1),"s", flush=True)

# the newer f5_tts loads weights separately
LC = UI.load_checkpoint
print("load_checkpoint signature:", inspect.signature(LC), flush=True)
lc_ok = False
for attempt in (
    lambda: LC(model, ckpt, device="cpu"),
    lambda: LC(model, ckpt_file=ckpt, device="cpu"),
    lambda: LC(model, ckpt),
    lambda: LC(model, ckpt_file=ckpt),
):
    try:
        r = attempt()
        model = r if r is not None else model
        lc_ok = True
        print("checkpoint loaded", flush=True)
        break
    except Exception as e:
        print("  lc attempt failed:", str(e)[:120], flush=True)
if not lc_ok:
    print("WARNING: could not load checkpoint, model may be random", flush=True)
model = model.to("cpu").eval()

vparams = inspect.signature(load_vocoder).parameters
vkw = {}
for k, v in dict(vocoder_name="vocos", is_local=False, local_path=None, device="cpu").items():
    if k in vparams: vkw[k] = v
vocoder = load_vocoder(**vkw)
print("vocoder loaded", flush=True)

SR=24000; pieces=[]
for i,c in enumerate(chunks,1):
    t1=time.time()
    ip = inspect.signature(infer_process).parameters
    ikw = {}
    for k, v in dict(mel_spec_type="vocos", device="cpu", show_info=print).items():
        if k in ip: ikw[k] = v
    wav, sr, spec = infer_process(REF_WAV, ref_text, c, model, vocoder, **ikw)
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
