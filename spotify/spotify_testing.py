# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# <h1>Compilation of Medium articles and other websites.<h1>
# 
# https://medium.com/@maxtingle/getting-started-with-spotifys-api-spotipy-197c3dc6353b
# 
# https://towardsdatascience.com/how-to-create-large-music-datasets-using-spotipy-40e7242cc6a6 : https://github.com/MaxHilsdorf/introduction_to_spotipy
# 
# https://morioh.com/p/31b8a607b2b0
# 

# %%
# sleep_min = 2
# sleep_max = 5
# start_time = time.time()
# request_count = 0
# for i in spotify_albums:
#     audio_features(i)
#     request_count+=1
#     if request_count % 5 == 0:
#         print(str(request_count) + " playlists completed")
#         time.sleep(np.random.uniform(sleep_min, sleep_max))
#         print('Loop #: {}'.format(request_count))
#         print('Elapsed Time: {} seconds'.format(time.time() - start_time))


# %%
# spotipy libraries
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials


# %%
# other libraries
import time
from decouple import config


# %%
# data visualisation libraries
import pandas as pd
import numpy as np
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# %%
# env variables
client_id = config('SPOTIPY_CLIENT_ID')
client_secret = config('SPOTIPY_CLIENT_SECRET')


# %%
# spotipy object
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager= client_credentials_manager)


# %%
# my user id
my_user = 'sidsaxena'


# %%
# function to analyse all tracks in a playlist by its ID and create a dataframe with audio features 

def analysePlaylist(creator, playlist_id):
    
    # Create empty dataframe
    playlist_features_list = ["artist","album","track_name",  "track_id","danceability","energy","key","loudness","mode", "speechiness","instrumentalness","liveness","valence","tempo", "duration_ms","time_signature"]
    
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    # Loop through every track in the playlist, extract features and append the features to the playlist df
    
    playlist = sp.user_playlist_tracks(creator, playlist_id)["items"]
    for track in playlist:        # Create empty dict
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
        
    return playlist_df


# %%
# get list of a user's playlists
my_playlists = sp.user_playlists(my_user)
my_playlists_items = my_playlists['items']


# %%
# playlist names, ids and their owners
name_list = [item['name'] for item in my_playlists_items]
id_list = [item['id'] for item in my_playlists_items]
creator_list = [my_playlists_items[item]['owner']['id'] for item in range(0, len(my_playlists_items))]


# %%
# a tuple of the playlist owners and the playlist ids
creator_id_tuple = tuple(zip(creator_list, id_list))


# %%
# dictionary of playlist name as key and ids and owners as tuple
pd_dict = dict(name = name_list, id = id_list, creator = creator_list)
pd_df = pd.DataFrame(pd_dict)


# %%
#dictionary with playlist names as key and creator id tuples as values
multiple_playlist_dict = dict(zip(name_list, creator_id_tuple))


# %%
#function to analyse multiple playlists (dicts) and return a dataframe.

def analysePlaylistDict(playlist_dict):
    
    # Loop through every playlist in the dict and analyze it
    for i, (key, val) in enumerate(playlist_dict.items()):
        time.sleep(.5)
        playlist_df = analysePlaylist(*val)
        # Add a playlist column so that we can see which playlist a track belongs too
        playlist_df["playlist"] = key
        # Create or concat df
        if i == 0:
            playlist_dict_df = playlist_df
        else:
            playlist_dict_df = pd.concat([playlist_dict_df, playlist_df], ignore_index = True)
            
    return playlist_dict_df


# %%
#multiple_playlist_df = analyze_playlist_dict(multiple_playlist_dict)


# %%
# function to get track ids from a playlist and return id list.

def getTrackIds(user, playlist_id):
    ids = []
    playlist = sp.user_playlist(user, playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    return ids

# ids = getTrackIds(my_user, vfar_id)


# %%
# function to get features of a track by its ID.

def getTrackFeatures(id):
    meta = sp.track(id)
    features = sp.audio_features(id)

    #meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']

    #features
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    key = features[0]['key']
    loudness = features[0]['loudness']
    mode = features[0]['mode']
    speechiness = features[0]['speechiness']
    acousticness = features[0]['acousticness']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    valence = features[0]['valence']
    tempo = features[0]['tempo']
    time_signature = features[0]['time_signature']

    track = [name, album, artist, release_date, length, popularity,danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature]
    return track


# %%
# function to get features of multiple tracks from a list of IDs and return a dataframe

def getTracklistFeatures(tracklist):
  # loop over track ids 
  tracks = []
  for id in range(len(ids)):
    time.sleep(.5)
    track = getTrackFeatures(tracklist[id])
    tracks.append(track)

  # create dataset
  df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speech', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'])
  # df.to_csv("spotify.csv", sep = ',')
  return df

# %% [markdown]
# <h1> GET ARTIST'S ALBUMS <h1>

# %%
#function to get discography of an artist by searching its name

def getDiscography(name):
    search = sp.search(q=name, type='artist')
    search = search['artists']['items'][0]

    search_id = search['id']
    search_albums = sp.artist_albums(search_id, album_type='album')

    album_names = []
    album_id = []
    for i, _ in enumerate(search_albums['items']):
        album_names.append(search_albums['items'][i]['name'])
        album_id.append(search_albums['items'][i]['id'])
    
    tracklist = []
    album_list = []
    track_album_dict = {}
    track_id = []

    for album, _ in enumerate(album_id):
        tracks = sp.album_tracks(album_id[album])
        tracks = tracks['items']
        album_name = sp.album(album_id[album])['name'] 
        for track, _ in enumerate(tracks):
            track_name = tracks[track]['name']
            track_id.append(tracks[track]['id']) 
            tracklist.append(track_name)
            album_list.append(album_name)       
    
    track_album_dict = {'track': tracklist, 'album': album_list, 'id': track_id}     
    df = pd.DataFrame(track_album_dict)

    return df


