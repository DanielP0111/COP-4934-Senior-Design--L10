# Certificate and Key Information
Due to the research nature of this project, both keys and certificates are provided to users to easily set up the DocTalk Infrastructure on demand. However, these keys and certificates expire in 365 days (March 2027). At that point, users can use the notes below to generate their own keys. Instructions are broken down to a 'per communication channel' basis. 

## Agent to Ollama container encryption
Apparently my ollama certs were missing a Subject ALternative Name (SAN), Creating the openssl.cnf file and using this command to generate new certs fixed this.

```
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout ollama-key.pem \
  -out ollama-cert.pem \
  -config openssl.cnf \
  -extensions req_ext
```

## Agent to MySQL container encryption
```
openssl genrsa 2048 > mysql-ca-key.pem

openssl req -new -x509 -nodes -days 3650 \
  -key mysql-ca-key.pem \
  -out mysql-ca.pem \
  -subj "/CN=MySQL-CA"
```

```
openssl req -newkey rsa:2048 -nodes \
  -keyout mysql-server-key.pem \
  -out mysql-server-req.pem \
  -subj "/CN=mysql"
```

```
openssl x509 -req \
  -in mysql-server-req.pem \
  -days 3650 \
  -CA mysql-ca.pem \
  -CAkey mysql-ca-key.pem \
  -set_serial 01 \
  -out mysql-server-cert.pem
```
## Agent to WebUI container encryption

```
openssl req -x509 -newkey rsa:2048 \
  -keyout agents-key.pem \
  -out agents-cert.pem \
  -days 365 \
  -nodes \
  -subj "/CN=agents"
```