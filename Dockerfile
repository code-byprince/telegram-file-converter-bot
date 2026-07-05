FROM python:3.11-slim

# System dependencies:
# - poppler-utils -> pdf2image ke liye zaroori (PDF -> Image)
# - ffmpeg        -> video/audio conversion ke liye zaroori
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Temp folder jaha files process hongi
RUN mkdir -p /app/temp

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
