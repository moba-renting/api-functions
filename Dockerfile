FROM python:3.12-slim as builder
WORKDIR /app
RUN python -m venv .venv
COPY requirements.txt .
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim as runtime
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD uvicorn main:app --host 0.0.0.0 --port $PORT