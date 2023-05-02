'''
 encoding: UTF-8
 python: 3.9.13

 Author: Dako Dimov, Lyuboslav Angelov
 Date: 21.04.2023 (v1.0)    - Initial release.
 Date: 02.05.2023 (v1.1)    - Added logging and fixed items with no download events.
 Date: 02.05.2023 (v1.2)    - Added check for estimated time ramaining.
 
 Version: 1.1
'''

# Import RadarrAPI Class
from pyarr import RadarrAPI
from datetime import datetime as dt
from datetime import timedelta as tdelta

import logging
import sys
import requests

# Set Host URL and API-Key
host_url = '<YOUR RADARR ADDRESS HERE>'

# You can find your API key in Settings > General.
api_key = '<YOUR API KEY HERE>'

# How long should the release be in the queue, before it gets replaced.
time_limit = tdelta(hours=0, days=1)

# How long to wait before checking the estimated remaining time until the release is downloaded.
when_to_start_checking_time_remaining = tdelta(hours=1, days=0)

# The maximum allowed estimated remaining time until the release is downloaded.
max_allowed_time_remaining = tdelta(hours=0, days=1)

# Logging
log_file = './RadarrStalledCleaner.log'


def get_radarr(host_url, api_key):
    """Returns an instance of the Radarr API client.

    Args:
        host_url (str): The URL of the Radarr server.
        api_key (str): The API key for the Radarr server.

    Returns:
        RadarrAPI: An instance of the Radarr API client.

    Raises:
        requests.ConnectionError: If the connection to the Radarr server fails.
        requests.exceptions.SSLError: If an SSL error occurs while connecting to the Radarr server.
        Exception: If any other error occurs while connecting to the Radarr server.
    """
    try:
        radarr = RadarrAPI(host_url, api_key)
        return radarr
    except requests.ConnectionError as e:
        logging.warning('Unable to connect to server: %s', e.strerror)
        sys.exit(1)
    except requests.exceptions.SSLError as e:
        logging.fatal('SSL error %s', e)
        sys.exit(1)
    except Exception as e:
        logging.warning('Unhandled exception: %s', e)
        sys.exit(1)


def get_queued_movies(radarr):
    """Get all movies in download queue (Activity tab).

    Args:
        radarr (Radarr): An instance of the Radarr API client.
    Returns:
        list[dict[str, any]]: A list of dictionaries containing details about movies in the queue.
    """
    try:
        queued_movies = radarr.get_queue_details()
        return queued_movies
    except requests.ConnectionError as e:
        logging.fatal('Unable to connect to server: %s', e.strerror)
        sys.exit(1)
    except requests.exceptions.SSLError as e:
        logging.fatal('SSL error %s', e)
        sys.exit(1)
    except Exception as e:
        logging.fatal('Unhandled exception: %s', e)
        sys.exit(1)


def delete_movie_download(radarr, movie_download):
    """Removes a movie download from the queue in Radarr.

    Args:
        radarr (Radarr): An instance of the Radarr API client.
        movie_download (dict): A dictionary representing the movie download to remove from the queue.

    Raises:
        BaseException: If an error occurs when removing the movie download from the queue.
    """
    resp = requests.Response()
    try:
        resp = radarr.del_queue(movie_download['id'],True,True)
    except BaseException as e:
        logging.critical('Error when removing from queue %s', e)
        return
    if resp != 200:
        logging.error('Error removing stale movie "%s"', movie_download['title'])
        logging.debug('Error: %s', resp)
    else:
        logging.info('Removed stale movie download: ', movie_download['title'] )
        logging.debug('Removed stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                    movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])



def main(args):

    logging.basicConfig(filename =  log_file,
                        level =     logging.DEBUG,
                        datefmt =   '%Y-%m-%d %H:%M:%S',
                        format =    u'%(asctime)s %(levelname)-8s %(message)s'
                        )
        
    radarr = get_radarr(host_url, api_key)
    queued_movies = get_queued_movies(radarr)

    for movie_download in queued_movies:

        # Ignore movie if it is not being downloaded.
        if movie_download['status'] != 'downloading':
            logging.info('Skipping "%s" - Status "%s" is not a downloading status.',
                         movie_download['title'], movie_download['status'])
            continue

        # Get when the movie was grabbed.
        grab_events = radarr.get_movie_history(movie_download['movieId'], 'grabbed')

        if len(grab_events) <= 0:
            # log error
            logging.error('Movie "%s" has no history of being grabbed.', movie_download['title'])
            continue

        # Sort by grab date.
        grab_events.sort(key=lambda event: event['date'],reverse=True)
        last_grab_event = grab_events[0]
        
        # Debug print
        for evt in grab_events:
            time_delta = dt.now() - dt.strptime(evt['date'], '%Y-%m-%dT%H:%M:%SZ')
            logging.debug('%s --- %s --- %s', evt['date'], movie_download['title'], time_delta)
        
        # Get time elapsed from last grab.
        time_elapsed = dt.now() - dt.strptime(last_grab_event['date'], '%Y-%m-%dT%H:%M:%SZ')

        # Delete movie download and blacklist release if remaining time is too long
        if time_elapsed > when_to_start_checking_time_remaining:
            completion_time = dt.strptime(movie_download['estimatedCompletionTime'], '%Y-%m-%dT%H:%M:%SZ')
            remaining_time = completion_time - dt.now()
            if remaining_time > max_allowed_time_remaining:
                logging.info('Removing stale download, time remaining is too long: %s - %s',
                             remaining_time, movie_download['title'])
                logging.debug('Removing stale movie title, time remaining is too long: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])
                delete_movie_download(radarr, movie_download)

        # Delete movie download and blacklist release if elapsed time is too long
        if time_elapsed > time_limit:
            logging.info('Removing stale movie download: %s', movie_download['title'] )
            
            logging.debug('Removing stale movie title: %s (ID: %d), queue ID: %d, grab event id: %d: ',
                           movie_download['title'], movie_download['movieId'], movie_download['id'], last_grab_event['id'])
            
            delete_movie_download(radarr, movie_download)


if __name__ == '__main__':
    main(sys.argv)
