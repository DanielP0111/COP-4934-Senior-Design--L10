# agentic-ai-security
This README is specifically for the Kali Linux container located in the compose.yaml file. The purpose of this container is to be used as a workstation and hacking toolset.

# The Kali Linux Workstation

## The Compose File
In the compose.yaml file, the following code snippet responsible for the Kali container is visible.

```yaml
kali:
    build:
      context: ./startup
      dockerfile: Dockerfile.kali
    image: kali-image # Just the name, not the actual image
    container_name: kali-linux
    stdin_open: true
    tty: true
    networks: 
      - billnet
```

- The above code snippet creates a Docker container utilizing the Dockerfile.kali Dockerfile, located in the startup folder. 
- The image is named “kali-image” yet utilizes the Dockerfile to create the actual full image on startup.
- The container is simply named “kali-container”
-  stdin_open: true Stops the container form exiting immediately
-  tty: true Creates an interactive session with the container, so that it may be accessed as a terminal at any time
- Lastly, the workstation is placed upon our network, named billnet, so that it may interact with other containers on the network

## The Dockerfile
To help us build our Kali-Linux image, we will utilize an associated Dockerfile. This Dockerfile is named “Dockerfile.kali”. 
```dockerfile
FROM docker.io/kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iputils-ping \
    curl \
    nmap \
    net-tools \
    tshark \
    ffuf \
    bettercap \
    sqlmap

WORKDIR /root
```

- Inside the Dockerfile, we will simply pull the latest Kali Linux image from docker.io as a baseline. 
- We then make the workstation noninteractive, so that packet installation may progress without user input
- As the default image is somewhat barebones, we will use a RUN command to install a few helpful tools on startup.

### Included Tools
- iputils-ping - Used to check if an address is reachable
- curl - Multipurpose tool for data transfer and API testing
- nmap - Network scanner and recon tool
- net-stat - Need netstat, a local network recon tool
- tshark - Packet capturer
- ffuf - Web fuzzer for pen testing
- bettercap - Man in the middle toolset
- sqlmap - SQL injection testing tool

## Accessing the container
After running the following code to startup all of the containers in the compose file:
```bash
docker compose up -d
```
You may enter into the Kali workstation terminal by running the following command:
 ```bash
docker exec -it kali-linux bash
```
To exit, simply enter:
```bash
exit
```

Once inside the workstation, you may use any of the installed tools as you would normally. Happy hacking!
