FROM python:2.7-slim
WORKDIR /app
COPY . .
RUN pip install -e .
ENTRYPOINT [ "zcashd-miner.py" ]