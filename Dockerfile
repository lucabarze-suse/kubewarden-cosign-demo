FROM registry.suse.com/bci/python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

USER 65532:65532

CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
