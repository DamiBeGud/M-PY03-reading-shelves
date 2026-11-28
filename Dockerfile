FROM python:3.12-slim-bookworm AS prepared
WORKDIR /app
COPY . .
RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
FROM prepared AS test
RUN ["python", "-m", "pytest"]
FROM prepared AS runtime
USER 10001:10001
EXPOSE 8203
ENTRYPOINT []
CMD ["python", "-c", "import os, subprocess, sys; subprocess.run([sys.executable, \"-m\", sys.argv[1]], check=True, timeout=60); os.execvp(sys.argv[2], sys.argv[2:])", "reading_shelves.migrate", "uvicorn", "reading_shelves.app:app", "--host", "0.0.0.0", "--port", "8203"]
