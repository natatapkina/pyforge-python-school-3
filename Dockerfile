FROM python:3.12-slim

# copy requirements in root folder
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
WORKDIR /app
COPY /app/ .

CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "--reload", "main:app"]