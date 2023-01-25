FROM python:3.10-slim as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt
FROM base
COPY --from=builder /install /usr/local
COPY ./ /app
WORKDIR /app
CMD ["python3", "-u", "main.py"]