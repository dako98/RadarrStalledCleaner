FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD [ "python", "./RadarrStalledCleaner.py" ]

RUN apt-get update && apt-get install -y cron && apt-get clean
COPY example-crontab /etc/cron.d/example-crontab
RUN chmod 0644 /etc/cron.d/example-crontab && crontab /etc/cron.d/example-crontab

CMD python ./RadarrStalledCleaner.py && cron && tail -f /dev/null