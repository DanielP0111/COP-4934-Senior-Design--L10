# Certificate and Key Information
Due to the research nature of this project, both keys and certificates are provided to users to easily set up the DocTalk Infrastructure on demand. However, these keys and certificates expire in 365 days (March 2027). At that point, users can use the notes below to generate their own keys.


## Full Command and Notes
A singular Certificate Authority (CA) is created and then each service gets a certificate (signed by the CA) and a key generated. Because the Ollama container doesn't natively support HTTPS, an HTTPS proxy was set up to handle encryption. To complete this successfully, the Ollama certificate and key were generated using a openssl.conf file (included in the repo) that assigns an alternative DNS name (proxy and ollama).


```
openssl genrsa -out ca-key.pem 4096
openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 -subj "/CN=billnet-CA" -out ca.pem

openssl genrsa -out agents-key.pem 2048
openssl req -new -key agents-key.pem -subj "/CN=agents" -out agents.csr
openssl x509 -req -in agents.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out agents-cert.pem -days 825 -sha256

openssl genrsa -out ollama-key.pem 2048
openssl req -new -key ollama-key.pem -out ollama.csr -config openssl.conf
openssl x509 -req -in ollama.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out ollama-cert.pem -days 825 -sha256 -extfile openssl.conf -extensions req_ext

openssl genrsa -out mysql-server-key.pem 2048
openssl req -new -key mysql-server-key.pem -subj "/CN=mysql" -out mysql-server.csr
openssl x509 -req -in mysql-server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out mysql-server-cert.pem -days 825 -sha256
cp ca.pem mysql-ca.pem  # MySQL client just needs the CA cert
```

After generation, *.csr files will be generated. These can be ignored or deleted. 