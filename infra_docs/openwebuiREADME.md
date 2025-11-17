# agentic-ai-security
This README is specifically for the Open WebUI container located in the compose.yaml file. The purpose of this container is to serve as the interface for user's to interact with the agentic system.

# The Open WebUI Interface

## The Compose File
In the compose.yaml file, the following code snippet responsible for the Open WebUI container is visible.

```yaml
open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    environment:
      - DEFAULT_USER_ROLE=admin
      - WEBUI_AUTH=False
      - WEBUI_NAME=DocTalk
      - WEBUI_PORT=8080
      - WEBUI_HOST=0.0.0.0
      - OPENAI_API_BASE_URL=http://python_container:8000/v1
      - ENABLE_TITLE_GENERATION=False
      - ENABLE_FOLLOW_UP_GENERATION=False
      - ENABLE_AUTOCOMPLETE_GENERATION=False
      - ENABLE_EVALUATION_ARENA_MODEL=False
      - ENABLE_TAGS_GENERATION=False
      - ENABLE_OLLAMA_API=False
    ports:
      - "3000:8080"
    volumes:
      - ./data:/app/backend/data
      - ./config:/app/backend/config
      - ./design/themes:/app/backend/open_webui/static:ro
      - ./design/build:/app/build:ro
    networks: 
      - billnet
    depends_on:
      - ollama
      - python_container
    restart: unless-stopped
```

- The above code snippet creates a Docker container utilizing the open-webui image from the GitHub Container Registry. 
- The container is simply named “open-webui”
- The default user role is set to `admin`, allowing the user to make changes to settings within Open WebUI.
- Authentication is set to `False` so that the user does not have to log in to the site.
- The name of the site is set to `DocTalk`.
- The port is set to `8080`, which is where in the container the service will run.
- Host is set to `0.0.0.0` so that the service is available to all IPs.
- The OpenAI base url is set to `http://python_container:8000/v1` which overrides the default model so that the custom orchestrator endpoint is used.
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

## Setting up the Model Connection
- Inside of the Open WebUI interface, navigate to the **Admin Panel** in the top right of the screen.
- From there, navigate to **Settings -> Connections**.
- Here you should see `http://python_container:8000/v1` under OpenAI API.
- Click on the gear icon to the right of this URL to configure the model connection.
- In the **Edit Connection** window, add the model ID, "doc_talk" and save.
- Now, when you navigate back to **New Chat**, you should see the "doc_talk" model and you can begin messaging the agents.