FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
COPY requirements-base.txt .

RUN pip install -r requirements.txt
RUN pip install -r requirements-base.txt
RUN apt-get update && apt-get install -y \
    build-essential \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
