FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -t /usr/src/app

COPY . .

RUN crontab -l | { cat; echo "* * * * * cd /usr/src/app && python3 /usr/src/app/RadarrStalledCleaner.py"; } | crontab -

CMD python ./RadarrStalledCleaner.py && crond && tail -f /dev/null