# kali-container test environment

This folder contains a small docker-compose test environment to run the AI orchestration scripts (`agentscripts/orchestration.py`) against a lightweight mock model service. The goal is to provide a repeatable, no-cost test harness for development and CI.

## What this sets up

- `python-app` — the existing `python-container` image built from the repository `Dockerfile`. It mounts `./agentscripts` to `/app/agentscripts` so you can iterate on scripts without rebuilding.
- `mysql` — local MySQL used by the repo (same as before).
- `ubuntu` — utility container if you need a general shell in the network.
- `ai-mock` — a tiny FastAPI-based mock model server that implements `/v1/health` and `/v1/chat/completions` compatible responses.

## How to run (repeatable)

1. Build and start the compose stack (from this directory):

```bash
docker compose up -d --build
```

2. Confirm the mock is healthy:

```bash
docker compose exec ai-mock curl -fsS http://localhost:11434/v1/health
# should print {"status":"ok"}
```

3. Run the orchestration script from the `python-container` (persistent deps are installed in the image):

```bash
# execute inside the running python-container
docker exec -it python-container /bin/sh -c \
  "export MODEL_BASE_URL=http://ai-mock:11434/v1 MODEL_NAME=qwen2.5:3b-instruct OPENAI_API_KEY=ollama; \
   python /app/agentscripts/orchestration.py"

### Using a lightweight Alpine container

If you prefer a minimal vanilla Alpine-based container to host and run the AI scripts (smaller image), the compose stack now includes an `alpine-python` service based on `python:3.11-alpine` that mounts `./agentscripts`.

Start the stack and exec into the Alpine container:

```bash
docker compose up -d --build
docker exec -it alpine-python /bin/sh
```

From inside the container you can run the orchestration script with the correct environment variables pointing it to the mock model service:

```bash
export MODEL_BASE_URL=http://ai-mock:11434/v1 MODEL_NAME=qwen2.5:3b-instruct OPENAI_API_KEY=ollama
python /app/agentscripts/orchestration.py
```

The `alpine-python` service now builds a small image that installs the repository `requirements.txt` so you won't need to pip-install manually every run. If you change `kali-container/requirements.txt`, rebuild the service with:

```bash
docker compose build alpine-python
docker compose up -d alpine-python
```
```

Notes:
- `python-container` is built from the `kali-container/Dockerfile` which now installs `requirements.txt`. If you edit `requirements.txt`, rebuild with `docker compose build python-app`.
- If you prefer ephemeral runs (no rebuild), use the `docker run --network ... python:3.11-slim` pattern we used earlier and `pip install` on the fly.

## Files added

- `docker/mock/Dockerfile` — small uvicorn server image
- `docker/mock/app.py` — FastAPI mock for `/v1/chat/completions`
- `docker/mock/requirements.txt` — Python deps for mock
- `README.md` — this doc

## Next steps / recommendations

- If you want deterministic termination during integration tests, update the mock to return a termination token after N messages or modify `orchestration.py` to enforce a max-iteration count.
- If you want CI integration, add a small test that starts the compose stack and runs the orchestration for 1-2 cycles.
