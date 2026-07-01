# hw07 tool server — optional container (hw07-tool-server).
# Running on the host with uvicorn works too; see README.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tools_server.py .

EXPOSE 5005
CMD ["uvicorn", "tools_server:app", "--host", "0.0.0.0", "--port", "5005"]
