import pygame
from pygame import mixer
from mutagen.mp3 import MP3
import mutagen.easyid3 as easyid3
from sys import argv
from os import name, walk
from os.path import expanduser

if len(argv[1:]) < 1:
    print("""Usage: python newnewmain.py <songs> [args]
    \"--shuffle\": shuffle the songs list
    \"--help\": print this help and exit""")
    exit()

for arg in argv[1:]:
    if "--help" in arg:
        print("""Usage: python newnewmain.py <songs> [args]
            \"--shuffle\": shuffle the songs list
            \"--loop=[all/song]\": loop the songs list or singular song respectivly
            \"--help\": print this help and exit""")
        exit()

if name == "linux":
    for arg in argv:
        if "--temp-dir" in arg:
            temp = arg.split("=")
            TEMP_DIR = temp[1]
        else:
            TEMP_DIR = "~/.temp"

elif name == "nt":
    for arg in argv:
        if "--temp-dir" in arg:
            temp = arg.split("=")
            TEMP_DIR = temp[1]
        else:
            TEMP_DIR = expanduser("~") + "/.temp"

class Song():
    def __init__(self, path):
        self.path = path
        self.cover = self.getCover()
        self.title = self.getTitle()
        self.artist = self.getArtist()
        self.length = self.getLen()

    def getCover(self):
        """
        Gets cover data from metadata of mp3 at APIC:Cover
        :return: cover binary data
        """
        audio = MP3(self.path)
        cover = audio.tags.get("APIC:Cover")
        return cover.data

    def getTitle(self) -> str:
        """
        Gets title from metadata of mp3 at id3:title
        :return: title;
        """
        audio = MP3(self.path, ID3=easyid3)
        title = audio.info.title
        return title

    def getArtist(self) -> str:
        """
        Gets artist from metadata of mp3 at id3:artist
        :return: first artist in artists;
        """
        audio = MP3(self.path, ID3=easyid3)
        artist = audio.info.artist[0]
        return artist
    def getLen(self) -> float:
        """
        Gets length from metadata of mp3 at id3:length in SECONDS
        :return: length of file from metadata;
        """
        audio = MP3(self.path)
        length = audio.info.length()
        return length

class Manager:
    def __init__(self, width: int = 800, height: int = 800):
        pygame.display.init()
        self.display = pygame.display.set_mode((width, height))
        self.songs = []
        self.isPaused = False
        self.isLooping = False
        self.songQueuePosition = 0
        self.currentSong = None

    def getSongs(self, query):
        if query == "all" or query == "*":
            for i in walk("./"):
                print(i)
    def selectSong(self):
        self.currentSong = Song(self.songs[self.songQueuePosition])

    def displayCover(self):
        pass

    def liveCaption(self):
        pass

    def pausePlay(self):
        pass

    def skipNextSong(self):
        pass

    def skipPrevSong(self):
        pass


manager = Manager()
manager.getSongs("all")