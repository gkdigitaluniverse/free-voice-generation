# Reference videos — 10 picked from the three channels

Listed live with yt-dlp on 2026-11-22. Downloads on GitHub are blocked by
YouTube's bot check ("Sign in to confirm you're not a bot"), which is a
datacenter-IP block, not a yt-dlp bug. Use the Termux block at the bottom.

## @explivolt — 2 videos only (channel has just two long videos)
| id | duration | title |
|---|---|---|
| ezxA4BuMRfM | 9:01 | How to Create Hindi Reels with Claude Code (Full Tutorial) — Write a Topic, Reel Ready |
| taxKAPHj38w | 6:35 | The iPhone 18 Pro Camera Has Moving Blades. Here's What They Do. |

## @puretechlens — 4 videos
| id | duration | title |
|---|---|---|
| ofXS6uog6nU | 6:55 | Traveling Salesman Problem, P vs NP, NP-Hard and NP-Complete Explained Like An 8th Grader |
| tUOiHJN4hPM | 6:28 | Why Quantum Computers Could Change Everything |
| IziJL_7O080 | 6:02 | Why AI Sounds Confident (But Could be Wrong) — Easy Explanation |
| muse5f9JMX0 | 5:17 | Fable Built an AI Property Manager App to Replace My Real Property Manager |

## @insiderforce — 4 videos (shorts only, no videos tab)
| id | title |
|---|---|
| Tjkk7rFqYPQ | Cursor, Codex, Claude Code Users: How to Get Your Whole Team on One AI Agent With Shared Skills |
| iL7T0P48i-A | How to Build and Sell Full Apps With AI Agents Running Your Business 24/7, No Code Needed |
| jlPVufdNQm4 | ChatGPT Can Now Create and Run a Professional AI Influencer Using CapCut |
| IDe-B7UEojs | How to Automate Your Entire Business With an AI Agent, No Code Needed |

## Termux — one block, copy paste whole thing

```bash
pkg update -y && pkg install -y python ffmpeg && pip install -U yt-dlp && termux-setup-storage && mkdir -p "/storage/emulated/0/Venter/HopWeb/Projects/12111" && cd "/storage/emulated/0/Venter/HopWeb/Projects/12111" && yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 -o "%(id)s_%(title).60s.%(ext)s" --no-playlist --retries 5 "https://www.youtube.com/watch?v=ezxA4BuMRfM" "https://www.youtube.com/watch?v=taxKAPHj38w" "https://www.youtube.com/watch?v=ofXS6uog6nU" "https://www.youtube.com/watch?v=tUOiHJN4hPM" "https://www.youtube.com/watch?v=IziJL_7O080" "https://www.youtube.com/watch?v=muse5f9JMX0" "https://www.youtube.com/watch?v=Tjkk7rFqYPQ" "https://www.youtube.com/watch?v=iL7T0P48i-A" "https://www.youtube.com/watch?v=jlPVufdNQm4" "https://www.youtube.com/watch?v=IDe-B7UEojs"
```

Note: the folder you wrote was `.../Projects/12111वह/`. I used `12111`. If the real
name is different, change it in the mkdir and cd parts.
