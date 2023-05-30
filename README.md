# Radarr Stalled Cleaner

## About

Radarr Stalled Cleaner aims to keep you from getting stuck on slow or incomplete downloads by setting a limit on how long a grabbed release should take to download. If the time limit is exceeded, the download gets removed and the release is blocklisted in Radarr. After that, Radarr is instructed to search for a new release.

## Install

The script assumes that you have Python 3 already installed.
To install the required dependencies for the script, run:  
 `pip install -r ./requirements.txt`

## Setup

Inside the script there are 3 variables you have to change, depending on yoursetup:
* host_url - the address of your Radarr instance  
Example 1: `host_url = 'https://example.com/'`  
Example 2: `host_url = 'http://127.0.0.1:7878/'`
* api_key - this is your Radarr API key. You can find your API key in Radarr by going to Settings > General.  
Example: `api_key = 'abc123d4ef567hij8kl91011mn12'`
* time_limit - what is the maximum time allowed for a download to complete.  
Eexample: `time_limit = tdelta(weeks=0, days=1, hours=0, minutes=0)`

## Use

Typical usage of this script would be to run it on a schedule. To do that in a GNU/Linux system using cron jobs, run:  
```
crontab -l > mycron  
echo "0 0 * * * python3 /home/user/scripts/RadarrStalledCleaner.py" >> mycron  
crontab mycron  
rm mycron
```
Where `/home/user/scripts/RadarrStalledCleaner.py` is the path to the script. This will run it every day at midnight.

## Advanced

By default the script will log its actions in a subfolder called "logs". Optionally, you can can change the path to the log file and the logging level.  
The log file is set with the variable `log_file = './logs/RadarrStalledCleaner.log'` and the logging level is set by `log_level = logging.INFO`