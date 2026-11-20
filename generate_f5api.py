import os, re, subprocess, sys, time, inspect
import numpy as np, soundfile as sf

REF_SRC="voice-reference.mp3"; REF_WAV="ref.wav"; OUT="output.mp3"
GAP_MS=110
SCRIPT = sys.argv[1] if len(sys.argv)>1 else "script.txt"

# mood -> (cfg_strength, speed)
MOODS = {
  "excited": (2.2, 1.22),
  "calm":    (1.8, 1.18),
  "serious": (2.0, 1.16),
  "warning": (2.3, 1.10),
}
NFE = 16

def parse_script(path):
    out=[]
    for line in open(path, encoding="utf-8"):
        line=line.strip()
        if not line: continue
        m=re.match(r'\[(\w+)\]\s*(.+)', line)
        if m: out.append((m.group(1).lower(), m.group(2).strip()))
        else: out.append(("calm", line))
    return out

subprocess.run(["ffmpeg","-y","-v","error","-ss","0.15","-t","7.4","-i",REF_SRC,
                "-ar","24000","-ac","1","-c:a","pcm_s16le",REF_WAV], check=True)
ref_text=open("ref_text.txt",encoding="utf-8").read().strip()
items=parse_script(SCRIPT)
print("script:", SCRIPT, "| chunks:", len(items), flush=True)
for i,(m,t) in enumerate(items,1): print(f"  {i}. [{m}] {t[:50]}", flush=True)

t0=time.time()
from huggingface_hub import hf_hub_download
vocab = hf_hub_download("ai4bharat/IndicF5", "checkpoints/vocab.txt")
ckpt  = hf_hub_download("Saravananravi/indicf5-hinglish", "model.safetensors")
print("weights:", os.path.getsize(ckpt), flush=True)

import torch
from f5_tts.model import DiT
import f5_tts.infer.utils_infer as UI

cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)
p = inspect.signature(UI.load_model).parameters
kw = {k:v for k,v in dict(mel_spec_type="vocos", vocab_file=vocab, ode_method="euler", use_ema=True, device="cpu").items() if k in p}
model = UI.load_model(DiT, cfg, **kw)
UI.load_checkpoint(model, ckpt, device="cpu")
model = model.to("cpu").eval()
vkw = {k:v for k,v in dict(vocoder_name="vocos", is_local=False, local_path=None, device="cpu").items()
       if k in inspect.signature(UI.load_vocoder).parameters}
vocoder = UI.load_vocoder(**vkw)
print("model + vocoder ready in", round(time.time()-t0,1),"s", flush=True)

SR=24000; pieces=[]
for i,(mood,txt) in enumerate(items,1):
    cs, spd = MOODS.get(mood, MOODS["calm"])
    t1=time.time()
    ip = inspect.signature(UI.infer_process).parameters
    ikw = {k:v for k,v in dict(mel_spec_type="vocos", device="cpu", show_info=lambda *a,**k: None,
            cfg_strength=cs, speed=spd, nfe_step=NFE).items() if k in ip}
    wav, sr, spec = UI.infer_process(REF_WAV, ref_text, txt, model, vocoder, **ikw)
    a=np.array(wav, dtype=np.float32).squeeze()
    if sr!=SR:
        sf.write("t.wav", a, sr)
        subprocess.run(["ffmpeg","-y","-v","error","-i","t.wav","-ar",str(SR),"-ac","1","t2.wav"], check=False)
        a,sr=sf.read("t2.wav", dtype="float32")
    dur=len(a)/SR
    print(f"  chunk {i} [{mood} cs={cs} sp={spd} nfe={NFE}]: {dur:.1f}s in {round(time.time()-t1,1)}s", flush=True)
    pieces.append(a.astype(np.float32)); pieces.append(np.zeros(int(SR*GAP_MS/1000),dtype=np.float32))

audio=np.concatenate(pieces) if pieces else np.zeros(SR,dtype=np.float32)
print("raw total:", round(len(audio)/SR,2),"s", flush=True)
sf.write("raw.wav", audio, SR)

# pitch +2 semitones without changing tempo, trim pauses to 0.15s, denoise, normalise
r = 2 ** (2/12)
subprocess.run(["ffmpeg","-y","-v","error","-i","raw.wav","-af",
  f"asetrate={int(SR*r)},aresample={SR},atempo={1/r:.6f},"
  "silenceremove=stop_periods=-1:stop_duration=0.15:stop_threshold=-38dB,"
  "highpass=f=75,afftdn=nf=-28,loudnorm=I=-15:TP=-1.5:LRA=11",
  "-ar",str(SR),"-ac","1","-b:a","128k",OUT], check=False)
print("SAVED", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else 0, flush=True)
