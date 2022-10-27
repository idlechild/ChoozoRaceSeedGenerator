FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ChoozoRaceSeedGenerator.py ChoozoRaceSeedGenerator.py
COPY smvaria.py smvaria.py

CMD ["python3", "ChoozoRaceSeedGenerator.py"]

