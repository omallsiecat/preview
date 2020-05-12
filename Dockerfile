FROM python:3.8

RUN apt update

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Secret Decryption
ADD https://static.ada.support/_infra/secrets/install.6f259cd.sh /tmp/install.sh
RUN chmod +x /tmp/install.sh && /tmp/install.sh && rm /tmp/install.sh

ADD https://static.ada.support/_infra/secrets/decrypt.6f259cd.sh /usr/local/bin/decrypt
RUN chmod +x /usr/local/bin/decrypt

COPY entrypoint.sh /usr/local/bin/entrypoint

ENTRYPOINT ["/usr/local/bin/entrypoint"]

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000", "--worker-class", "gevent", "--access-logfile", "-", "--log-level", "info", "--log-syslog"]
