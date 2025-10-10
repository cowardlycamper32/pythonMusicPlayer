import pygame
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from sys import argv
from os import name, listdir, getcwd
from os.path import expanduser, join
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
        print(self.path)

    def getCover(self):
        """
        Gets cover data from metadata of mp3 at APIC:Cover
        :return: cover binary data
        """
        try:
            audio = MP3(self.path)
            cover = audio.tags.get("APIC:Cover")
            return cover.data
        except AttributeError:
            return open(manager.getExecDir() + "images/placeholder.png", "rb").read()

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
        self.loopType = None
        self.songQueuePosition = 0
        self.currentSong = None
        self.shuffle = False
        self.songEnd = False
        self.volume = 1
        self.muted = False

    def getSongs(self, query):
        if query == "all" or query == "*":
            for i in listdir("./"):
                if ".mp3" in i:
                    self.songs.append(i)
        else:
            self.songs.append(query)
        self.shuffledSongs = self.songs
    def selectSong(self):
        self.songEnd = False
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
        if self.songQueuePosition + 1 > len(self.shuffledSongs) and self.isLooping is False:
            pass
        elif (self.songQueuePosition + 1 > len(self.shuffledSongs) and self.isLooping is True and self.loopType == "all"):
            self.songQueuePosition = 0
        elif self.songQueuePosition + 1 <= len(self.shuffledSongs):
            self.songQueuePosition += 1
        self.songEnd = True

    def skipPrevSong(self):
        if self.songQueuePosition - 1 < 0 and self.isLooping is False:
            pass
        elif (self.songQueuePosition - 1 < 0 and self.isLooping is True and self.loopType == "all"):
            self.songQueuePosition = len(self.shuffledSongs) - 1
        elif self.songQueuePosition - 1 >= 0:
            self.songQueuePosition -= 1
        self.songEnd = True

    def restartSong(self):
        self.songEnd = True

    def volumeDown(self, ammount=0.1):
        if self.volume - ammount <= 0:
            self.volume = 0
            mixer.music.set_volume(self.volume)
        else:
            self.volume -= ammount

            mixer.music.set_volume(self.volume)
        if self.muted:
            self.muted = False

    def volumeUp(self, ammount=0.1):
        if self.volume + ammount >= 1:
            self.volume = 1
            mixer.music.set_volume(self.volume)
        else:
            self.volume += ammount
            mixer.music.set_volume(self.volume)
        if self.muted:
            self.muted = False

    def volumeMute(self):
        if not self.muted:
            mixer.music.set_volume(0)
        else:
            mixer.music.set_volume(self.volume)
        self.muted = not self.muted

    def isSongEnd(self):
        if int(mixer.music.get_pos()/1000) >= int(self.currentSong.length):
            self.skipNextSong()
            self.songEnded = True

    def getExecDir(self):
        temp = __file__.split(delimiter)
        temp.pop(-1)
        out = ""
        for i in temp:
            out += i + "/"
        return out

    def displayTimeline(self):
        frac = ((mixer.music.get_pos()+1)/1000) / self.currentSong.length
        print(frac)
        if frac < 0.0020:
            frac = 0.0021
        pygame.draw.line(self.display, (255, 0, 0), (100, 600), (700, 600), 10)
        shape = pygame.draw.line(self.display, (0, 255, 0), (100, 600), (100+(600*frac), 600), 10)


    def displayIcons(self):
        # Volume Icons
        if 0.8 < self.volume <= 1:
            if self.muted:
                icon = "volumeMuted1"
            else:
                icon = "volume1"
        elif 0.6 < self.volume <= 0.8:
            if self.muted:
                icon = "volumeMuted2"
            else:
                icon = "volume2"
        elif 0.4 < self.volume <= 0.6:
            if self.muted:
                icon = "volumeMuted3"
            else:
                icon = "volume3"
        elif 0.2 < self.volume <= 0.4:
            if self.muted:
                icon = "volumeMuted4"
            else:
                icon = "volume4"
        elif 0 < self.volume <= 0.2:
            if self.muted:
                icon = "volumeMuted5"
            else:
                icon = "volume5"
        else:
            if self.muted:
                icon = "volumeMuted5"
            else:
                icon = "volume6"
        image = pygame.image.load(self.getExecDir() + "images/" + icon + ".png")
        self.display.blit(image, (800-96-8, 400-20-8))
        # timeline
        self.displayTimeline()

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
        manager.selectSong()
        while (mixer.music.get_busy() or manager.isPaused) and not manager.songEnd:
            manager.display.fill((0, 0, 0))
            manager.displayCover()
            manager.displayIcons()
            pygame.display.update()
            manager.liveCaption()
            manager.isSongEnd()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                    if event.key == pygame.K_SPACE:
                        manager.pausePlay()

                    if event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if mixer.music.get_pos() > 5000:
                            manager.restartSong()
                        else:
                            manager.skipPrevSong()

                    if event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        manager.skipNextSong()

                    if event.key == pygame.K_UP:
                        manager.volumeUp()

                    if event.key == pygame.K_DOWN:
                        manager.volumeDown()

                    if event.key == pygame.K_m:
                        manager.volumeMute()

                    if event.key == pygame.K_s:
                        manager.shuffleSongs()