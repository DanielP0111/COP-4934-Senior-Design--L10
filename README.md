# agentic-ai-security
COP-4934-Senior-Design--L10. This repo is for group L10 of UCF's senior design 1 class. We will be working on security concerns in agentic AI systems

##Podman Web Server Set Up
1. podman build -t image-name .
2. podman create --name container-name -p 8080:80 image-name
3. podman start container-name
4. podman stop container-name