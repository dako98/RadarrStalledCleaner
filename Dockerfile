FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -t /usr/src/app

COPY . .

#ENV RADARR_URL="https://127.0.0.1:7878/"
#ENV RADARR_URL_BASE=""
#ENV RADARR_API_KEY=""
#ENV SCHEDULE="* * * * *"
#ENV LOG="./logs/RadarrStalledCleaner.log"
#ENV L_LEVEL="INFO"

RUN crontab -l | { cat; echo "${SCHEDULE} python3 /usr/src/app/RadarrStalledCleaner.py"; } | crontab -

CMD python ./RadarrStalledCleaner.py && crond && tail -f /dev/null