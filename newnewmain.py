import pygame
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from sys import argv
from os import name, listdir, getcwd
from os.path import expanduser
from pathlib import Path
import random
import time
userHome = str(Path.home())
DONTQUIT = True
cwd = getcwd()

if name == "posix":
    for arg in argv:
        if "--temp-dir" in arg:
            temp = arg.split("=")
            TEMP_DIR = temp[1]

        else:
            TEMP_DIR = userHome + "/.temp"
    delimiter = "/"

elif name == "nt":
    for arg in argv:
        if "--temp-dir" in arg:
            temp = arg.split("=")
            TEMP_DIR = temp[1]
        else:
            print(expanduser("~/.temp"))
            TEMP_DIR = expanduser("~/.temp")
    delimiter = "\\"
else:
    TEMP_DIR = None

HELP_MENU = f"""Usage: python newnewmain.py <songs> [args]
        \"--shuffle\": shuffle the songs list
        \"--loop=[all/song]\": loop the songs list or singular song respectively
        \"--temp-dir=[directory]\": set the temporary directory to ssomewhere other than \"{TEMP_DIR}\"
        \"--help\": print this help and exit"""
if len(argv[1:]) < 1:
    print(HELP_MENU)
    exit()





class Song():
    def __init__(self, path):
        self.path = cwd + delimiter + path
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
        try:
            audio = MP3(self.path, ID3=EasyID3)
            title = audio.tags["title"]
            return title[0]
        except:
            return self.path.split(delimiter)[-1]

    def getArtist(self) -> str:
        """
        Gets artist from metadata of mp3 at id3:artist
        :return: first artist in artists;
        """
        try:
            audio = MP3(self.path, ID3=EasyID3)
            artist = audio.tags["artist"]
            return artist[0]
        except:
            return "Unknown Artist"
    def getLen(self) -> float:
        """
        Gets length from metadata of mp3 at id3:length in SECONDS
        :return: length of file from metadata;
        """
        audio = MP3(self.path)
        length = audio.info.length
        return length
    def load(self):
        mixer.music.load(self.path)
        mixer.music.play()

class Manager:
    def __init__(self, width: int = 800, height: int = 800):
        pygame.display.init()
        mixer.init()
        self.display = pygame.display.set_mode((width, height))
        self.songs = []
        self.shuffledSongs = []
        self.isPaused = False
        self.isLooping = False
        self.songQueuePosition = 0
        self.currentSong = None
        self.shuffle = False
        self.songEnd = False

    def getSongs(self, query):
        if query == "all" or query == "*":
            for i in listdir("./"):
                if ".mp3" in i:
                    self.songs.append(i)
        else:
            self.songs.append(query)
        self.shuffledSongs = self.songs
    def selectSong(self):
        self.currentSong = Song(self.shuffledSongs[self.songQueuePosition])
        print(self.currentSong.path)
        self.currentSong.load()
        #self.pausePlay()


    def shuffleSongs(self):
        if self.shuffle:
            self.shuffledSongs = self.songs
            self.shuffle = False
        else:
            random.shuffle(self.shuffledSongs)
            self.shuffle = True

    def displayCover(self):
        cover = self.currentSong.getCover()
        open(TEMP_DIR + "/cover.png", "wb").write(cover)

        try:
            image = pygame.image.load(TEMP_DIR + "/cover.png")
        except pygame.error:
            print(
                '''Cannot load image:''', name)
            raise SystemExit
        image = image.convert()
        self.display.blit(pygame.transform.scale(image, self.display.get_size()), (0, 0))


    def liveCaption(self):
        pygame.display.set_caption(f"{self.currentSong.title} - {self.currentSong.artist}")

    def pausePlay(self):
        if self.isPaused:
            mixer.music.unpause()
        else:
            mixer.music.pause()
        self.isPaused = not self.isPaused

    def skipNextSong(self):
        pass

    def skipPrevSong(self):
        pass
mixer.init()
manager = Manager()
manager.getSongs("all")
for arg in argv[1:]:
    if "--help" in arg:
        print(HELP_MENU)
        exit()
    if "--shuffle" in arg:
        manager.shuffleSongs()
while DONTQUIT:
    for song in manager.shuffledSongs:
        while (mixer.get_busy() or not manager.isPaused) and DONTQUIT:
            manager.selectSong()
            manager.displayCover()
            pygame.display.update()
            manager.liveCaption()
            mixer.music.play()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        manager.pausePlay()