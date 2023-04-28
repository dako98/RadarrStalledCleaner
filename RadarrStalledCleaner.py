'''
 encoding: UTF-8
 python: 3.9.13

 Author: Dako Dimov
 Date: 21.04.2023 (v1.0)    - Initial release.
 
 Version: 1.0
'''

# Import RadarrAPI Class
from pyarr import RadarrAPI
from datetime import datetime as dt
from datetime import timedelta as tdelta

# Set Host URL and API-Key
host_url = '<YOUR RADARR ADDRESS HERE>'

# You can find your API key in Settings > General.
api_key = '<YOUR API KEY HERE>'

# How long should the release be in the queue, before it gets replaced.
time_limit = tdelta(hours=0, days=7)

# Instantiate RadarrAPI Object
radarr = RadarrAPI(host_url, api_key)

# Get all movies in download queue (Activity tab).
queued_movies = radarr.get_queue_details()


for movie_download in queued_movies:

    # Get when the movie was grabbed.
    grab_events = radarr.get_movie_history(movie_download['movieId'], 'grabbed')

    # Sort by grab date.
    grab_events.sort(key=lambda event: event['date'],reverse=True)
    last_grab_event = grab_events[0]
    
    # Get time elapsed from last grab.
    time_elapsed = dt.now() - dt.strptime(last_grab_event['date'], '%Y-%m-%dT%H:%M:%SZ')

    # If the grabbed release has reached the time limit - blacklist release and search for a new one.
    if time_elapsed > time_limit:
        print('Overdue: ', time_elapsed, ' - ', movie_download['title'])
        resp = radarr.del_queue(movie_download['id'],True,True)
        print(resp)
