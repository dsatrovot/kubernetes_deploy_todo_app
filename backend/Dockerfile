FROM python:3.12-slim

WORKDIR /backend_app

COPY src/requirements.txt /backend_app/

RUN --mount=type=cache,target=/root/.cache/pip pip install -r /backend_app/requirements.txt

COPY . /backend_app/

EXPOSE 8000

CMD ["uvicorn","src.main:app","--host", "0.0.0.0","--port","8000" ]
