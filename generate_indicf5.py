# indicf5 run 2
import os, re, subprocess, time
import numpy as np, soundfile as sf

REF_SRC="voice-reference.mp3"; REF_WAV="ref.wav"; OUT="output.mp3"
MAX_CHARS=110; GAP_MS=140

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
print("ref bytes:", os.path.getsize(REF_WAV))

chunks=split_script("script.txt"); print("chunks:", len(chunks))
t0=time.time()
from transformers import AutoModel
model=AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True)
print("model loaded in", round(time.time()-t0,1),"s")

SR=24000; pieces=[]
for i,c in enumerate(chunks,1):
    t1=time.time()
    a=np.array(model(c, ref_audio_path=REF_WAV, ref_text=ref_text))
    if a.dtype==np.int16: a=a.astype(np.float32)/32768.0
    a=a.astype(np.float32).squeeze(); dur=len(a)/SR
    if dur>16:
        print(f"  chunk {i}: {dur:.1f}s too long, retry")
        a=np.array(model(c, ref_audio_path=REF_WAV, ref_text=ref_text))
        if a.dtype==np.int16: a=a.astype(np.float32)/32768.0
        a=a.astype(np.float32).squeeze(); dur=len(a)/SR
    print(f"  chunk {i}: {dur:.1f}s in {round(time.time()-t1,1)}s")
    pieces.append(a); pieces.append(np.zeros(int(SR*GAP_MS/1000),dtype=np.float32))

audio=np.concatenate(pieces) if pieces else np.zeros(SR,dtype=np.float32)
print("raw total:", round(len(audio)/SR,2),"s")
sf.write("raw.wav", audio, SR)
subprocess.run(["ffmpeg","-y","-v","error","-i","raw.wav","-af",
  "silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB,highpass=f=70,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11",
  "-ar","24000","-ac","1","-b:a","96k",OUT], check=False)
print("SAVED", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else 0)
