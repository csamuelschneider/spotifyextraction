import requests
import pandas as pd
import config

playlist_url = 'https://open.spotify.com/playlist/3HpvkxzzB3K0TBZSlSdk47?si=e8db8f8f1db84f1e'

class extractData():
    offset = 0
    trackData = {}
    
    def __init__(self):
        
        self.authenticate()
        self.playlist_id = playlist_url.split('/')[-1].split('?')[0]
        self.playlist = self.apiCall(f'playlists/{self.playlist_id}/tracks')
        if self.playlist.status_code == 200:
            self.playlist = self.playlist.json()
            self.getPlaylistTracks(self.playlist)
            self.getAudioFeatures()
        self.dict_to_df()
        self.df_to_csv()
    
    def authenticate(self):
        
        authResponse = requests.post(config.auth_url, {
                'grant_type': 'client_credentials',
                'client_id': config.client_id,
                'client_secret': config.client_secret
        })
                                    
        authData = authResponse.json()
        authToken = authData['access_token']
        self.headers = {'Authorization': 'Bearer {token}'.format(token=authToken)}
        
    def apiCall(self, url_string, parameters=None):
        return requests.get(config.base_url + url_string, headers=self.headers, params=parameters)
    
    def getPlaylistTracks(self, playlist):  
        self.playlistTracks = playlist['items']
        while self.offset < playlist['total']:
            self.offset += 100
            playlist = self.apiCall(f'playlists/{self.playlist_id}/tracks', {'offset': self.offset}).json()
            for item in playlist['items']:
                self.playlistTracks.append(item)
                
    def getAudioFeatures(self):
        for item in range(len(self.playlistTracks)):
            track_id = self.playlistTracks[item]['track']['id']
            features = self.apiCall(f'audio-features/{track_id}').json()
            try:
                self.trackData[track_id] = {
                    'track_id': track_id,
                    'name': self.playlistTracks[item]['track']['name'],
                    'artist': self.playlistTracks[item]['track']['artists'][0]['name'],
                    'popularity': float(self.playlistTracks[item]['track']['popularity']),
                    'danceability': float(features['danceability']),
                    'valence': float(features['valence']),
                    'energy': float(features['energy']),
                    'loudness': float(features['loudness']),
                    'key': float(features['key']),
                    'mode': int(features['mode']),
                    'tempo': float(features['tempo']),
                    'duration_ms': int(features['duration_ms']),
                    'acousticness': float(features['acousticness'])               
                }
            except:
                continue

    def dict_to_df(self):
        self.trackDataDf = pd.DataFrame.from_dict(self.trackData, orient='index')


    def df_to_csv(self):
        path = 'whatavibe.csv'
        self.trackDataDf.to_csv(path, encoding= 'utf-8', decimal=',')


extractData()