FROM python:3.13-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures logs appear immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# System deps (keep minimal)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
