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
ckpt = hf_hub_download("ai4bharat/IndicF5", "model.safetensors")
vocab = hf_hub_download("ai4bharat/IndicF5", "checkpoints/vocab.txt")
print("weights:", ckpt, os.path.getsize(ckpt), flush=True)

from f5_tts.api import F5TTS
tts = F5TTS(model_type="F5-TTS", ckpt_file=ckpt, vocab_file=vocab,
            vocoder_name="vocos", device="cpu")
print("F5TTS loaded in", round(time.time()-t0,1), "s", flush=True)

SR=24000; pieces=[]
for i,c in enumerate(chunks,1):
    t1=time.time(); p=f"part{i}.wav"
    try:
        tts.infer(ref_file=REF_WAV, ref_text=ref_text, gen_text=c, file_wave=p, show_info=print)
    except Exception as e:
        print("chunk",i,"FAILED:",str(e)[:300], flush=True); raise
    a,sr=sf.read(p, dtype="float32")
    if sr!=SR:
        subprocess.run(["ffmpeg","-y","-v","error","-i",p,"-ar",str(SR),"-ac","1",p], check=False)
        a,sr=sf.read(p, dtype="float32")
    a=a.squeeze().astype(np.float32); dur=len(a)/SR
    print(f"  chunk {i}: {dur:.1f}s in {round(time.time()-t1,1)}s", flush=True)
    pieces.append(a); pieces.append(np.zeros(int(SR*GAP_MS/1000),dtype=np.float32))

audio=np.concatenate(pieces) if pieces else np.zeros(SR,dtype=np.float32)
print("raw total:", round(len(audio)/SR,2),"s", flush=True)
sf.write("raw.wav", audio, SR)
subprocess.run(["ffmpeg","-y","-v","error","-i","raw.wav","-af",
  "silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB,highpass=f=70,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11",
  "-ar","24000","-ac","1","-b:a","96k",OUT], check=False)
print("SAVED", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else 0, flush=True)
