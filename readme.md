## Overview

A simple dockerless transcription tool using OpenAI's WHisper model. Gets transcription, but not speaker labels.

Assuming UV is installed

```python
uv venv
source .venv/bin/activate
uv pip sync requirements.txt 

python3 transcribe_local.py <path to file>
```
