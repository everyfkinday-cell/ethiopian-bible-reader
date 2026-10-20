FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY public ./public
COPY tts_voices ./tts_voices

ENV PORT=7860
EXPOSE 7860

CMD ["python3", "app.py"]
