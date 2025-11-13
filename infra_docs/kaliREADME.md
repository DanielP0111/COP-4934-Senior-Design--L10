# agentic-ai-security
This README is specifically for the Kali Linux container located in the compose.yaml file. The purpose of this container is to be used as a workstation and hacking toolset.

# The Kali Linux Workstation

## The Compose File
In the compose.yaml file, the following code snippet responsible for the Kali container is visible.

```yaml
kali:
    build:
      context: ./autogen
      dockerfile: Dockerfile.kali
    image: kali-image # Just the name, not the actual image
    container_name: kali-linux
    stdin_open: true
    tty: true
    networks: 
      - billnet
```

- The above code snippet creates a Docker container utilizing the Dockerfile.kali Dockerfile, located in the autogen folder. 
- The image is named “kali-image” yet utilizes the Dockerfile as the image used upon creation.
-  stdin_open: true Stops the container form exiting immediately
-  tty: true Creates an interactive session with the container, so that it may be accessed as a terminal at any time
- Lastly, the workstation is placed upon our network, named billnet, so that it may interact with other containers on the network

## The Dockerfile
To help us build our Kali-Linux image, we will utilize an associated Dockerfile. This Dockerfile is named “Dockerfile.kali”. 
- Inside the Dockerfile, we will simply pull the latest mysql image from docker.io as a baseline. 
- As the default image is somewhat barebones, we will use a RUN command to install a few helpful tools on startup.

### Included tools
- iputils-ping - Used to check if an address is reachable
- curl - Multipurpose tool for data transfer and API testing
- nmap - Network scanner and recon tool
- net-stat - Need netstat, a local network recon tool
- tshark - Packet capturer
- ffuf - Web fuzzer for pen testing
- bettercap - Man in the middle toolset
- sqlmap - SQL injection testing tool

# Accessing the container
After running the following code to startup all of the containers in the compose file:
```bash
docker compose up -d
```
You may enter into the Kali workstation terminal by running the following command:
 ```bash
docker exec -it kali-linux bash
```
Once inside the workstation, you may use any of the installed tools as you would normally. Happy hacking!
