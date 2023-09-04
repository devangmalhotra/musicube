# Local file creator (Musicube)
# 1. Get title and artist of YouTube video (pytube3)
# 2. Check if song exists on Apple Music API (or iTunes, not sure yet) from YouTube based on Title and artist (iGetMusic)
# 3. Get important info (Title, Artist, Album, Album Artist, Genre, Year, Track#)
# 4. Get cover art
# 5. Add file to iTunes app (will probably only work on Mac)

from pytube import YouTube, streams
import iGetMusic as iGet
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2
import eyed3
from eyed3.id3.frames import ImageFrame
import requests
from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sys import platform
from pathlib import Path
import os
from configparser import ConfigParser

def calculation_with_metadata(vid_link):
    #config file
    file = 'config.ini'
    config = ConfigParser()
    config.read(file)

    #Authentication for Spotipy - without user
    client_credentials_manager = SpotifyClientCredentials(client_id=config['spotipy_details']['id'], client_secret=config['spotipy_details']['secret'])
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    downloads_path = str(Path.home() / "Downloads") # ONLY WORKS ON MAC AS OF NOW

    # Extracting title and artist from YouTube video
    yt = YouTube(vid_link)
    title_yt = yt.title
    artist_yt = yt.author

    song_for_cover = iGet.get(term=title_yt + " " + artist_yt, limit=1, country="GB", explicit=True) 
    song = sp.search(q=title_yt + artist_yt, limit=1 , type='track')
    song_to_select = song_for_cover[0] # Choose first result in search


    title = song['tracks']['items'][0]['name'] # Choose first result in search # title of song
    artist = song['tracks']['items'][0]['artists'][0]['name'] # artist of song
    album = song['tracks']['items'][0]['album']['name']
    track_num = song['tracks']['items'][0]['track_number']
    disc_num = song['tracks']['items'][0]['disc_number']
    year = str(yt.publish_date)[0:4]

    artist_obj = iGet.getArtist(term=artist, country="GB", explicit=True)
    artist_to_select = artist_obj[0]
    genre = (artist_to_select.getGenre())[0]

    # accessing audio streams of YouTube obj.(first one, more available)
    # downloading a video would be: stream = yt.streams.first()
    yt.streams.filter(progressive=True).get_highest_resolution().download(f'{downloads_path}', filename=f'{artist} - {title}.mp4') # downloads video
    video = VideoFileClip(f'{downloads_path}/{artist} - {title}.mp4')
    video.audio.write_audiofile(f'{downloads_path}/{artist} - {title}.mp3') # converts video mp4 to audio mp3

    audiot = EasyID3(f"{downloads_path}/{artist} - {title}.mp3")
    audiot.delete()
    audiot['title'] = title
    audiot['artist'] = artist
    audiot['album'] = album
    audiot['tracknumber'] = str(track_num)
    audiot['discnumber'] = str(disc_num)

    if audiot['album'] == audiot['title']:
        audiot['album'] = f"{title} - Single"
        
    audiot['albumartist'] = artist
    audiot['genre'] = genre
    audiot['date'] = year
    audiot['encodedby'] = "Powered By Musicube"
    audiot.save()

    audiox = eyed3.load(f"{downloads_path}/{artist} - {title}.mp3")
    if audiox.tag is None:
        audiox.initTag()

    artwork_link = song['tracks']['items'][0]['album']['images'][0]['url']
    r = requests.get(artwork_link)
    fh = open(f'{downloads_path}/temp-album-art.jpg', "wb")
    fh.write(r.content)
    fh.close()

    audiox.tag.images.set(ImageFrame.FRONT_COVER, open(f'{downloads_path}/temp-album-art.jpg','rb').read(), 'image/jpeg')
    audiox.tag.save() 

    os.remove(f'{downloads_path}/temp-album-art.jpg')
    os.remove(f'{downloads_path}/{artist} - {title}.mp4')