# syntax=docker/dockerfile:1

FROM python:3.9.5-windowsservercore-1809

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 6000
CMD [ "python3", "./process_data/send_data_email.py"]
