# free-voice-generation

Hindi voice cloning with ResembleAI/chatterbox, running on GitHub Actions CPU.

- `script.txt` — the text to speak
- `voice-reference.mp3` — the voice to clone (18s is trimmed automatically)
- `generate.py` — generates output.mp3
- Push a change to `script.txt` and the workflow runs by itself.
- The result appears as a release asset named `voice`.

Model: ResembleAI/chatterbox (MIT). Please only clone voices you own or have permission to use.
