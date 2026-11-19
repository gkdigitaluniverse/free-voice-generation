import os, subprocess, sys, time
# keep the reference short: chatterbox prefers 10-20s
subprocess.run(["ffmpeg","-y","-v","error","-i","voice-reference.mp3","-t","18","-ac","1","-ar","24000","ref.wav"], check=False)
ref = "ref.wav" if os.path.exists("ref.wav") else "voice-reference.mp3"
text = open("script.txt", encoding="utf-8").read().strip()
t0=time.time()
try:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    wav = m.generate(text, language_id="hi", audio_prompt_path=ref)
    sr = m.sr
    print("multilingual OK")
except Exception as e:
    print("multilingual failed:", str(e)[:300])
    from chatterbox.tts import ChatterboxTTS
    m = ChatterboxTTS.from_pretrained(device="cpu")
    wav = m.generate(text, audio_prompt_path=ref)
    sr = m.sr
    print("base model OK (english model, may struggle with hindi)")
import torchaudio
torchaudio.save("output.mp3", wav, sr)
print("SAVED output.mp3", round(wav.shape[-1]/sr,2), "s in", round(time.time()-t0,1), "s")
