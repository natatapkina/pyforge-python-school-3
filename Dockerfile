FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
COPY /src/main.py .
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--reload", "main:app"]