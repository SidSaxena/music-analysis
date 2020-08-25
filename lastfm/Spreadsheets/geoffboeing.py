# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import requests, json, requests_cache, time, datetime, pandas as pd 
from decouple import config


# %%
API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
CALLBACK = config('CALLBACK')
USER_AGENT = 'SidSaxena'

username = 'SidSaxena'


# %%
requests_cache.install_cache(cache_name='listening_history', expire_after=43200)


# %%
# rate limiting
pause_duration = 0.2


# %%
# from dataquest.py import lastfm_get


# %%
url = 'https://ws.audioscrobbler.com/2.0/?method={}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'
limit = 200
extended = 0
page = 1


# %%
headers = {'user-agent': USER_AGENT}


# %%
artist_names = []
track_names = []
play_counts = []

method = 'user.getTopTracks'
request_url = url.format(method, username, API_KEY, limit, extended, page)

response = requests.get(request_url).json()

for item in response['toptracks']['track']:
    artist_names.append(item['artist']['name'])
    track_names.append(item['name'])
    play_counts.append(item['playcount'])

top_tracks = pd.DataFrame()
top_tracks['artist'] = artist_names
top_tracks['track'] = track_names
top_tracks['play_count'] = play_counts
top_tracks.to_csv('lastfm_top_tracks.csv', index=None)
top_tracks.head()


# %%
method = 'user.gettopartists'
request_url = url.format(method, username, API_KEY, limit, extended, page)
artist_names = []
play_counts = []
response = requests.get(request_url).json()
for item in response['topartists']['artist']:
    artist_names.append(item['name'])
    play_counts.append(item['playcount'])

top_artists = pd.DataFrame()
top_artists['artist'] = artist_names
top_artists['play_count'] = play_counts
top_artists.to_csv('lastfm_top_artists.csv', index=None)
top_artists.head()


# %%
method = 'user.getTopAlbums'
request_url = url.format(method, username, API_KEY, limit, extended, page)
artist_names = []
album_names = []
play_counts = []
response = requests.get(request_url).json()
for item in response['topalbums']['album']:
    artist_names.append(item['artist']['name'])
    album_names.append(item['name'])
    play_counts.append(item['playcount'])

top_albums = pd.DataFrame()
top_albums['artist'] = artist_names
top_albums['album'] = album_names
top_albums['play_count'] = play_counts
top_albums.to_csv('lastfm_top_albums.csv', index=None)
top_albums.head()


# %%
def get_scrobbles(method='recenttracks', username=username, key=API_KEY, limit=200, extended=0, page=1, pages=0):

    #initialise lists and url for response
    url = 'https://ws.audioscrobbler.com/2.0/?method=user.get{}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'

    responses = []
    artist_names = []
    artist_mbids = []
    album_names = []
    album_mbids = []
    track_names = []
    track_mbids = []
    timestamps = []

    # make first request, just to get total number of pages
    request_url = url.format(method, username, API_KEY, limit, extended, page)
    response = requests.get(request_url).json()
    total_pages = int(response[method]['@attr']['totalPages'])
    if pages > 0:
        total_pages = min([total_pages, pages])

    print('{} total pages to retrieve'.format(total_pages))

    # request each range of data one at a time

    for page in range(1, int(total_pages) + 1, 1):
        if page % 10 == 0:
            print(page, end=' ')
        request_url = url.format(method, username, key, limit, extended, page)
        responses.append(requests.get(request_url))
        
        if not getattr(response, 'from_cache', False):
            time.sleep(pause_duration)
    
    # parse the fields
    for response in responses:
        scrobbles = response.json()
        for scrobble in scrobbles[method]['track']:
            if 'date' in scrobble.keys():
                artist_names.append(scrobble['artist']['#text'])
                artist_mbids.append(scrobble['artist']['mbid'])
                album_names.append(scrobble['album']['#text'])
                album_mbids.append(scrobble['album']['mbid'])
                track_names.append(scrobble['name'])
                track_mbids.append(scrobble['mbid'])
                timestamps.append(scrobble['date']['uts'])
    
    df = pd.DataFrame()
    df['artist'] = artist_names
    df['artist_mbid'] = artist_mbids
    df['album'] = album_names
    df['album_mbid'] = album_mbids
    df['track'] = track_names
    df['track_mbid'] = track_mbids
    df['timestamp'] = timestamps
    df['datetime'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')                
    return df


# %%
scrobbles = get_scrobbles(pages=0)


# %%
scrobbles.to_csv('{name}_scrobbles_{date}.csv'.format(name=username, date=datetime.date.today()), index=None)


