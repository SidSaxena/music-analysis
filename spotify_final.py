# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
# spotipy modules
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials


# %%
# other libraries
from decouple import config 
import time


# %%
# visualisation libraries
import pandas as pd
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# %%
# environment variables
client_id = config('SPOTIPY_CLIENT_ID')
client_secret = config('SPOTIPY_CLIENT_SECRET')
redirect_uri = 'http://google.com/'


# %%
# authorization
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)


# %%
username = 'sidsaxena'


# %%
scope = 'playlist-read-private user-library-read user-top-read user-read-recently-played user-follow-read user-read-currently-playing'


# %%
try:
    
    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret= client_secret, redirect_uri=redirect_uri)
    sp = spotipy.Spotify(auth=token)

except:

    print('Token not accessible for user: ', username)


# %%
def getUserPlaylists(user):

    name_list = []
    id_list = []
    creator_list = []
    offset=0
    playlists = []

    while True:
        results = sp.user_playlists(user, offset=offset)
        playlists += results['items']

        if results['next'] is not None:
            offset += 50
        else:
            break

    for playlist, _ in enumerate(playlists):
        name_list.append(playlists[playlist]['name'])
        id_list.append(playlists[playlist]['id'])
        creator_list.append(playlists[playlist]['owner']['id'])
    
    creator_id_tuple = tuple(zip(creator_list, id_list))

    playlist_dict = dict(name = name_list, id = id_list, creator = creator_list)
        
    playlist_df = pd.DataFrame(playlist_dict)
    multiple_playlist_dict = list(creator_id_tuple)
    playlist_df.to_csv('{}-playlists.csv'.format(user))
    return playlist_df, multiple_playlist_dict


# %%
def analysePlaylist(creator, playlist_id):
    
    tracks = []
    offset = 0
    # Create empty dataframe
    playlist_features_list = ["artist","album","track_name",  "track_id","danceability","energy","key","loudness","mode", "speechiness","instrumentalness","liveness","valence","tempo", "duration_ms","time_signature"]
    
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    # Loop through every track in the playlist, extract features and append the features to the playlist df
        
    while True:
        results = sp.user_playlist_tracks(creator, playlist_id, offset=offset)
        tracks += results['items']

        if results['next'] is not None:
            offset += 50
        else:
            break

    for track in tracks:        # Create empty dict
        playlist_features = {}        # Get metadata
        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]
        playlist_features["track_id"] = track["track"]["id"]
        
        # Get audio features
        audio_features = sp.audio_features(playlist_features["track_id"])[0]
        for feature in playlist_features_list[4:]:
            playlist_features[feature] = audio_features[feature]
        
        # Concat the dfs
        track_df = pd.DataFrame(playlist_features, index = [0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)
    
    playlist_df.to_csv('{}-{}.csv'.format(creator, playlist_id))
    return playlist_df


# %%
def analysePlaylistsList(playlist_tuple_list):
    """function to analyse multiple playlists"""

    for id, _ in enumerate(playlist_tuple_list):
        playlist_df = analysePlaylist(playlist_tuple_list[id][0], playlist_tuple_list[id][1])

        # playlist_df['playlist'] = PLAYLIST NAME

        if id == 0:
            playlist_tuple_df = playlist_df
        else:
            playlist_tuple_df = pd.concat([playlist_tuple_df, playlist_df], ignore_index=True)

        playlist_tuple_df.to_csv('multiple playlists.csv')
        return playlist_tuple_df


# %%
my_playlists_df, my_playlists_list = getUserPlaylists(username)


# %%
my_playlists_df


# %%
three_playlists = my_playlists_list[9:12]


# %%
three_playlists


# %%
test_df = analysePlaylist(username, 'spotify:playlist:6Tz22UKQCnp4rqu6dNzVm0')


# %%
multiple_playlists_df = analysePlaylistsList(three_playlists)


