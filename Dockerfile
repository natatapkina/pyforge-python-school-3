FROM python:3.12-slim

# copy requirements in root folder
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy alembic in root folder
COPY alembic.ini .

# copy project files
WORKDIR /app
COPY /app/ .

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--reload", "main:app"]