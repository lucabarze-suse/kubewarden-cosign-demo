FROM registry.suse.com/bci/python:3.11

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/lib64/python3.11/site-packages -type d -name 'tests' -exec rm -rf {} + && \
    find /usr/lib64/python3.11/site-packages -name '*.pyc' -delete && \
    rm -rf /root/.cache /tmp/*

COPY app.py .

EXPOSE 8080
USER 65532:65532

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
