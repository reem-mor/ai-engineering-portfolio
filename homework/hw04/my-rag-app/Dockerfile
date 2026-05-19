# Step 1 — base image: use slim Python for smaller size
FROM python:3.14-slim

# Step 2 — set working directory inside the container
WORKDIR /app

# Step 3 — copy requirements first (better layer caching)
COPY requirements.txt .

# Step 4 — install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5 — copy rest of your project into the container
COPY . .

# Step 6 — tell Docker which port your app listens on
EXPOSE 5000

# Step 7 — command to start the app when container runs
CMD ["python", "app.py"]