FROM python:3.9-slim

WORKDIR /app

# Copy only requirements first so Docker can cache this layer
COPY requirements.txt .

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app
COPY . .

CMD ["python", "main.py"]
