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
scope = 'ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control user-read-email user-read-private playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private user-library-modify user-library-read user-top-read user-read-playback-position user-read-recently-played user-follow-read user-follow-modify'


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
def getTrackIds(user, playlist_id):
    """get track ids from a playlist and return id list."""
    
    ids = []
    playlist = sp.user_playlist(user, playlist_id)
    for item in playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    return ids

# ids = getTrackIds(my_user, vfar_id)


# %%
def getTrackIdsFromAlbum(album_id):

    tracklist = []
    track_id_list = []

    results = sp.album_tracks(album_id)
    tracks = results['items']
    album_results = sp.album(album_id)
    album_name = album_results['name'] 
    album_tracks = album_results['tracks']
    for track, _ in enumerate(tracks):
        tracklist.append(tracks[track]['name'])
        track_id_list.append(tracks[track]['id']) 

    return track_id_list


# %%
def analysePlaylist(creator, playlist_id):
    
    tracks = []
    offset = 0
    # Create empty dataframe
    playlist_features_list = ['artist','album','track_name', 'track_id', 'popularity', 'genres', 'danceability','energy','key','loudness','mode', 'speechiness','instrumentalness','liveness','valence','tempo', 'duration_ms','time_signature']
    
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
    # Loop through every track in the playlist, extract features and append the features to the playlist df
        
    while True:
        results = sp.user_playlist_tracks(creator, playlist_id, offset=offset)
        tracks += results['items']

        if results['next'] is not None:
            offset += 100
        else:
            break

    for track in tracks:       
        
        artist = track['track']['album']['artists'][0]
        artist_id = artist['id']
        genre = sp.artist(artist_id)
        genres = genre['genres']

        playlist_features = {}        
        playlist_features['artist'] = artist['name']
        playlist_features['album'] = track['track']['album']['name']
        playlist_features['track_name'] = track['track']['name']
        playlist_features['track_id'] = track['track']['id']
        playlist_features['popularity'] = track['track']['popularity']
        playlist_features['genres'] = [genres]
    
        # Get audio features
        time.sleep(0.5)
        audio_features = sp.audio_features(playlist_features['track_id'])[0]
        for feature in playlist_features_list[6:]:
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
def getDiscography(name):
    """get discography of an artist by searching its name and return a dataframe and genres in a seperate variable"""

    release_date_list = []
    track_id_list = []   
    tracklist = []
    album_list = []    
    track_album_dict = {}

    album_names = []
    album_id = []
    album_release_date = []

    single_names = []
    single_id = []
    single_release_date = []

    results = sp.search(q=name, type='artist')
    artist = results['artists']['items'][0]

    artist_name = artist['name']
    artist_id = artist['id']
    artist_genres = artist['genres']

    artist_albums = sp.artist_albums(artist_id, album_type='album')
    albums = artist_albums['items']
    
    while artist_albums['next']:
        artist_albums = sp.next(artist_albums)
        albums.extend(artist_albums['items'])

    for album in albums:
        album_names.append(album['name'])
        album_id.append(album['id'])
        album_release_date.append(album['release_date'])

    
    artist_singles = sp.artist_albums(artist_id, album_type='single')
    singles = artist_singles['items']
    
    while artist_singles['next']:
        artist_singles = sp.next(artist_singles)
        singles.extend(results['items'])

    for single in singles:
        single_names.append(single['name'])
        single_id.append(single['id'])
        single_release_date.append(single['release_date'])


    # MUCH BETTER CODE but need to figure out a way to append release date.
    # for album in album_id:
    #     tracks = sp.album_tracks(album)
    #     tracks = tracks['items']
    #     album_name = sp.album(album)['name']
    #     for track in tracks:
    #         track_name = track['name']
    #         track_id_list.append(track['id'])
    #         tracklist.append(track_name)
    #         album_list.append(album_name)
    #         release_date_list.append(album_release_date[])


    for album, _ in enumerate(album_id):
        tracks = sp.album_tracks(album_id[album])
        tracks = tracks['items']
        album_name = sp.album(album_id[album])['name'] 
        for track, _ in enumerate(tracks):
            track_name = tracks[track]['name']
            track_id_list.append(tracks[track]['id']) 
            tracklist.append(track_name)
            album_list.append(album_name)
            release_date_list.append(album_release_date[album])
    
    for single, _ in enumerate(single_id):
        tracks = sp.album_tracks(single_id[single])
        tracks = tracks['items']
        single_name = sp.album(single_id[single])['name'] 
        for track, _ in enumerate(tracks):
            single_name = tracks[track]['name']
            track_id_list.append(tracks[track]['id']) 
            tracklist.append(single_name)
            album_list.append(single_name)
            release_date_list.append(single_release_date[single])

    


    track_album_dict = {'track': tracklist, 'album': album_list, 'release_date': release_date_list, 'id': track_id_list}  
    df = pd.DataFrame(track_album_dict)
    df.to_csv('{}-discog.csv'.format(artist['name']))
    return df


# %%
def getTrackFeatures(id):
    """get features of a track by its ID."""
    
    meta = sp.track(id)
    features = sp.audio_features(id)

    #meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    artist_id = meta['album']['artists'][0]['id']
    genre = sp.artist(artist_id)['genres']
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

    track = [name, album, artist, release_date, genre, length, popularity,danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature]

    return track


# %%
def getTracklistFeatures(tracklist):
    """get features of multiple tracks from a list of IDs and return a dataframe"""

  # loop over track ids 
    tracks = []
    for id in range(len(tracklist)):
        track = getTrackFeatures(tracklist[id])
        tracks.append(track)

  # create dataset
    df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'release_date', 'genres', 'length', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'])
    df.to_csv("tracklist-features.csv", sep = ',')
    return df


# %%
my_playlists_df, my_playlists_list = getUserPlaylists(username)


# %%
name = input('Enter Username: ')
playlistid = input('Enter Playlist ID: ')


