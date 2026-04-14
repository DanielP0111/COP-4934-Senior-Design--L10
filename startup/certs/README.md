# Certificate and Key Information
Due to the research nature of this project, all required keys and certificates are provided to simplify initial setup of the DocTalk infrastructure. 

However, these keys and certificates expire in 365 days (March 2027). At that point, users can use the notes below to generate their own keys.


## Public Key Infrastructure Generation Overview
This setup uses a single Certificate Authority (CA) to sign certificates for each service.

- A root CA is created first
- Each service (agents, Ollama proxy, MySQL) gets:
    - A private key
    - A certificate signed by the CA

Because the Ollama container does not natively support HTTPS, an HTTPS proxy is used to handle TLS encryption. The Ollama certificate includes Subject Alternative Names (SANs) (e.g., proxy, ollama) defined in the provided openssl.conf.

## Certificate Generation Commands
These commands must be executed in the 'certs' directory of this repository. 
```
# Create CA
openssl genrsa -out ca-key.pem 4096
openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 -subj "/CN=billnet-CA" -out ca.pem

# Create Agents certificate
openssl genrsa -out agents-key.pem 2048
openssl req -new -key agents-key.pem -subj "/CN=agents" -out agents.csr
openssl x509 -req -in agents.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out agents-cert.pem -days 825 -sha256

# Create Ollama proxy certificate
openssl genrsa -out ollama-key.pem 2048
openssl req -new -key ollama-key.pem -out ollama.csr -config openssl.conf
openssl x509 -req -in ollama.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out ollama-cert.pem -days 825 -sha256 -extfile openssl.conf -extensions req_ext

# Create MySQL certificate
openssl genrsa -out mysql-server-key.pem 2048
openssl req -new -key mysql-server-key.pem -subj "/CN=mysql" -out mysql-server.csr
openssl x509 -req -in mysql-server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out mysql-server-cert.pem -days 825 -sha256
cp ca.pem mysql-ca.pem
```
## Notes
- After generation, *.csr files will be generated. These can be ignored or deleted. 
- Ensure openssl.conf is present and has the correct file path when generating the Ollama certificate.