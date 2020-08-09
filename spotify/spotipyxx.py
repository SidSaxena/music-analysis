#spotipy tutorial by Ian on Youtube
#https://www.youtube.com/playlist?list=PLqgOPibB_QnzzcaOFYmY2cQjs35y0is9N

import os
import json
import sys
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError

#from decouple import config

#Get the username
username = sys.argv[1]
scope = 'playlist-read-private'
try:
    token = util.prompt_for_user_token(username, scope)
except: 
    os.remove(f'.cache-{username}')
    token = util.prompt_for_user_token(username, scope)

spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()
displayName = user['display_name']
followers = user['followers']['total']

while True:

    print()
    print(f'Welcome to Spotipy, {user}!')
    print(f' You have {str(followers)} followers')
    print()
    print('0 - Search for an artist')
    print('1 - exit')
    print()
    choice = input('Your choice: ')

    if choice == 0:
        print('0')

    elif choice == 1:
        break

#print(json.dumps(VARIABLE, sort_keys=True, indent=4))
