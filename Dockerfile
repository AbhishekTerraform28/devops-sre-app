# 1. Base lightweight Linux + Python 3.11
FROM python:3.11-slim

# 2. Container ke andar working directory
WORKDIR /workspace

# 3. Fast console logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4. Layer caching: requirements pehle
COPY app/requirements.txt /workspace/requirements.txt

# 5. Packages installation
RUN pip install --no-cache-dir -r requirements.txt

# 6. Source code copy
COPY app/ /workspace/app/

# 7. Port definition
EXPOSE 8000

# 8. Service start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]