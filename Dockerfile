FROM python:3.10-slim
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm -f /requirements.txt
COPY kd.py /usr/local/bin/kd
RUN chmod +x /usr/local/bin/kd
ENTRYPOINT ["/usr/local/bin/kd"]