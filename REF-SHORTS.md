# Reference SHORTS — 4 per channel, 4 channels

Listed live with yt-dlp on 2026-11-22 from each channel's /shorts tab.
Shorts only. No long videos.

## @explivolt

| id | title |
|---|---|
| `qFwZhBrMYhI` | Why AI runs on GPUs, not CPUs |
| `7Na5g1DRLY4` | 100 Mbps plan but only 12 MB/s download? It's not a scam, it's math |
| `YL6b6yWpIB0` | How a 16GB Mac beats a 32GB PC: unified memory explained |
| `q7a2bg5oTcM` | How Claude actually works: tokens, models, connectors and skills |

## @puretechlens

| id | title |
|---|---|
| `UFeAIQNe554` | Who is the smartest AI over 3 years? |
| `RVXro2c7tyE` | Paid AI Tools That You Can Replace for Free |
| `wtNj4nknR1M` | Claude Missed a Dangerous Command 1 in 3 Times |
| `yHsqBe4UdG0` | How to build a free AI sales team |

## @insiderforce

| id | title |
|---|---|
| `Tjkk7rFqYPQ` | Get Your Whole Team on One AI Agent With Shared Skills |
| `IDe-B7UEojs` | How to Automate Your Entire Business With an AI Agent |
| `qGuDcRRJAD4` | Top 5 Free Claude Code Plugins Every Vibe Coder Needs |
| `RKZOKc51wz4` | Free GitHub Repo That Could End Your AI API Bill Forever |

## @apnaaischool

| id | title |
|---|---|
| `g1cARoOA1Vs` | Turn Rough Ideas into Full Video Scripts with Gemini |
| `ErxYN7wf74o` | New Free AI Voice Generator: ElevenLabs Alternative |
| `dykqc8JZmSc` | How to Test 3 Thumbnails on YouTube Studio |
| `QFrDN2yvv4w` | 3 Secret AI Audio Tools Every Creator Needs |

## Termux — one block, copy paste whole thing

```bash
pkg update -y && pkg install -y python ffmpeg && pip install -U yt-dlp && termux-setup-storage && mkdir -p "/storage/emulated/0/Venter/HopWeb/Projects/12111" && cd "/storage/emulated/0/Venter/HopWeb/Projects/12111" && yt-dlp -f "bv*+ba/b" --merge-output-format mp4 -o "%(id)s_%(title).60s.%(ext)s" --no-playlist --retries 5 "https://www.youtube.com/watch?v=qFwZhBrMYhI" "https://www.youtube.com/watch?v=7Na5g1DRLY4" "https://www.youtube.com/watch?v=YL6b6yWpIB0" "https://www.youtube.com/watch?v=q7a2bg5oTcM" "https://www.youtube.com/watch?v=UFeAIQNe554" "https://www.youtube.com/watch?v=RVXro2c7tyE" "https://www.youtube.com/watch?v=wtNj4nknR1M" "https://www.youtube.com/watch?v=yHsqBe4UdG0" "https://www.youtube.com/watch?v=Tjkk7rFqYPQ" "https://www.youtube.com/watch?v=IDe-B7UEojs" "https://www.youtube.com/watch?v=qGuDcRRJAD4" "https://www.youtube.com/watch?v=RKZOKc51wz4" "https://www.youtube.com/watch?v=g1cARoOA1Vs" "https://www.youtube.com/watch?v=ErxYN7wf74o" "https://www.youtube.com/watch?v=dykqc8JZmSc" "https://www.youtube.com/watch?v=QFrDN2yvv4w"
```

`termux-setup-storage` shows a permission dialog — tap Allow, or nothing lands in storage.

16 shorts total. On a phone they download in a couple of minutes.
