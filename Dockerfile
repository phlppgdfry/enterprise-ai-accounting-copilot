FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.lock && pip install --no-deps . && useradd -u 10001 -m app && mkdir data && chown app:app data
USER app
EXPOSE 8000
CMD ["uvicorn", "accounting_copilot.api:app", "--host", "0.0.0.0", "--port", "8000"]
