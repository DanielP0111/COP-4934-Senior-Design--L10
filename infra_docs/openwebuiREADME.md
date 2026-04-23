# agentic-ai-security
This README is specifically for the Open WebUI container located in the compose.yaml file. The purpose of this container is to serve as the interface for user's to interact with the agentic system.

# The Open WebUI Interface

## The Compose File
In the compose.yaml file, the following code snippet responsible for the Open WebUI container is visible.

```yaml
webui:
    image: ghcr.io/open-webui/open-webui:0.8.10
    container_name: webui
    ports:
      - "3000:8080"
    networks: 
      - billnet
    volumes:
      - ./webui-data:/app/backend/data
      - ./startup/webui.db:/app/backend/data/webui.db
      - ./themes:/app/backend/open_webui/static:ro
    environment:
      - WEBUI_AUTH=True
      - ENABLE_LOGIN_FORM=True
      - ENABLE_SIGNUP=False
      - ENABLE_FORWARD_USER_INFO_HEADERS=True
      - WEBUI_PORT=8080
      - WEBUI_HOST=0.0.0.0
      - OPENAI_API_BASE_URL=http://agents:8000/v1
      - ENABLE_TITLE_GENERATION=False
      - ENABLE_FOLLOW_UP_GENERATION=False
      - ENABLE_AUTOCOMPLETE_GENERATION=False
      - ENABLE_EVALUATION_ARENA_MODEL=False
      - ENABLE_TAGS_GENERATION=False
      - ENABLE_OLLAMA_API=False
    depends_on:
      - ollama
      - agents
    restart: unless-stopped
```

- The above code snippet creates a Docker container utilizing the open-webui image from the GitHub Container Registry. 
- The container is simply named “open-webui”
- Authentication is set to `True` allowing the user to sign into an account and save their chat history.
- The name of the site is set to `DocTalk`.
- The port is set to `8080`, which is where in the container the service will run.
- Host is set to `0.0.0.0` so that the service is available to all IPs.
- The OpenAI base url is set to `http://agents:8000/v1` which overrides the default model so that the custom orchestrator endpoint is used.
- The rest of the environment variables disable built-in features that are not needed. 
- The container maps its port 8080 to the host port 3000. This makes the Open WebUI service available outside of the container
- `data` and `config` volumes provide persistent storage for Open WebUI. THese folders are automatically initialized and populated upon startup.
- `design/themes` and `design/build` volumes override the default Open WebUI styling.
- The container is connected to the `billnet` Docker network.
- This container depends on both ollama and python_container, meaning it will not start until these are running.

## Accessing the Container
After running the following code to startup all of the containers in the compose file:
```bash
docker compose up -d
```
You may access the interface at:
`http://localhost:3000`