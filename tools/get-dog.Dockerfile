# syntax=docker/dockerfile:1

FROM python:3.9.5-alpine3.12

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5000

CMD [ "python3", "./dog_transaction/real_time_trans.py"]
