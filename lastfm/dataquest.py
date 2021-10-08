import requests
import requests_cache
import json
import time
import os

from dotenv import load_dotenv, dotenv_values
config = dotenv_values(".env")
load_dotenv()

from tqdm import tqdm
tqdm.pandas()

from IPython.core.display import clear_output

requests_cache.install_cache()

API_KEY = os.environ.get('LAST_FM_API_KEY')
SHARED_SECRET = os.environ.get('LAST_FM_SHARED_SECRET')
CALLBACK = os.environ.get('LAST_FM_CALLBACK')

USER_AGENT = os.environ.get('LAST_FM_USER_AGENT')

def lastfm_get(payload):
    #define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'http://ws.audioscrobbler.com/2.0/'

    #api key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url=url, headers=headers, params=payload)
    return response

def jprint(obj):
    # create a formatted string from the json object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def getTopArtists():
        
    # empty list
    responses = []

    # inital page and high number of pages (wouldn't it result in an uneccesarily long loop?)
    page = 1
    total_pages = 99999

    while page < total_pages:
        payload = {
            'method': 'chart.gettopartists',
            'limit': 500,
            'page': page
        }

        #see status
        print('Requesting Page {}/{}'.format(page, total_pages))
        #clear output
        clear_output(wait=True)

        # make api call
        response = lastfm_get(payload)

        # if we get an error, print and halt
        if response.status_code != 200:
            print(response.text)
            break

        # extract pagination info
        page = int(response.json()['artists']['@attr']['page'])
        total_pages = int(response.json()['artists']['@attr']['totalPages'])

        # append response
        responses.append(response)

        # if not cached, sleep
        if not getattr(response, 'from_cache', False):
            time.sleep(0.25)

        page += 1

    return responses

responses = getTopArtists()

import pandas as pd

r0 = responses[0]
r0_json = responses[0].json()
r0_artists = r0_json['artists']['artist']
r0_df = pd.DataFrame(r0_artists)
r0_df.head() 

frames = [pd.DataFrame(r.json()['artists']['artist']) for r in responses]
artists = pd.concat(frames)
artists.info()

artists = artists.drop('image', axis=1)
artists.head()

artists.info()

artists.describe()

artist_counts = [len(r.json()['artists']['artist']) for r in responses]

pd.Series(artist_counts).value_counts()

print(artist_counts[:50])

artists = artists.drop_duplicates().reset_index(drop=True)
artists.describe()

def lookup_tags(artist):
    
    response = lastfm_get({
        'method': 'artist.getTopTags',
        'artist': artist
    })

    # if there's an error, return nothing
    if response.status_code != 200:
        return None
    
    # extract the top three tags and turn them into a string
    tags =[t['name'] for t in response.json()['toptags']['tag'][:3]]
    tags_str = ', '.join(tags)

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    
    return tags_str


artists['tags'] = artists['name'].progress_apply(lookup_tags)

# converting listeners and playcounts to int type

artists[["playcount", "listeners"]] = artists[["playcount", "listeners"]].astype(int)

# sorting by number of listeners

artists = artists.sort_values('listeners', ascending= False)

artists.to_csv('artists.csv', index=False)