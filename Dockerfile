FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system .

COPY . .

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
