FROM python:3.10-slim

WORKDIR /app

# 1. Install dependencies as root so packages install cleanly without permission errors
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 2. Setup non-root user (UID 1000 required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
COPY --chown=user . $HOME/app

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
