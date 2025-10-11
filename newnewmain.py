from os import system, name
from os.path import expanduser, join
from sys import argv
from pathlib import Path
userHome = str(Path.home())

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

temp = __file__.split(delimiter)
temp.pop(-1)
out = ""
for i in temp:
    out += i + "/"

try:
    system(f"{out}.venv/Scripts/activate")
except:
    system(f"python -m venv {out}.venv")
    system(f"{out}.venv/Scripts/activate")
try:
    import pygame
except:
    system("pip install pygame")
    import pygame
from pygame import mixer
try:
    from mutagen.mp3 import MP3
except:
    system("pip install mutagen")
    from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

from os import listdir, getcwd


import random
import time
try:
    from pynput import keyboard
except:
    system("pip install pynput")
    from pynput import keyboard


DONTQUIT = True
cwd = getcwd()



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
        #print(self.path)

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
        self.volumeTimer = 0
        self.inputTimer = 0
        self.inputListener = keyboard.Listener(on_press=self.onKeyPress)


    def onKeyPress(self, key):
        if key == keyboard.Key.media_next and self.inputTimer <= 0:
            self.inputTimer = 10
            self.skipNextSong()
        if key == keyboard.Key.media_previous and self.inputTimer <= 0:
            self.inputTimer = 10
            if mixer.music.get_pos() > 5000:
                self.restartSong()
            else:
                self.skipPrevSong()
        if key == keyboard.Key.media_play_pause and self.inputTimer <= 0:
            self.inputTimer = 10
            self.pausePlay()

    def startListener(self):
        self.inputListener.start()
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
        #print(self.currentSong.path)
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
        self.volumeTimer = 50
        if self.volume - ammount <= 0:
            self.volume = 0
            mixer.music.set_volume(self.volume)
        else:
            self.volume -= ammount

            mixer.music.set_volume(self.volume)
        if self.muted:
            self.muted = False

    def volumeUp(self, ammount=0.1):
        self.volumeTimer = 50
        if self.volume + ammount >= 1:
            self.volume = 1
            mixer.music.set_volume(self.volume)
        else:
            self.volume += ammount
            mixer.music.set_volume(self.volume)
        if self.muted:
            self.muted = False

    def volumeMute(self):
        self.volumeTimer = 50
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
        currentTime = mixer.music.get_pos()/1000
        frac = currentTime / self.currentSong.length
        #print(frac)
        if frac < 0.0020:
            frac = 0.0021
        pygame.draw.line(self.display, (36, 59, 97), (100, 600), (700, 600), 10)
        shape = pygame.draw.line(self.display, (56, 152, 255), (100, 600), (100+(600*frac), 600), 10)
        currentMins = int(currentTime / 60)
        currentSecs = int(currentTime % 60)
        fullMins = int(self.currentSong.length/60)
        fullSecs = int(self.currentSong.length % 60)
        if fullSecs < 10:
            fullSecs = "0" + str(fullSecs)
        if currentSecs < 10:
            currentSecs = "0" + str(currentSecs)
        currentTimeText = smallFont.render(f"{currentMins}:{currentSecs}", True, (65, 152, 255))
        fullTimeText = smallFont.render(f"{fullMins}:{fullSecs}", True, (65, 152, 255))
        self.display.blit(currentTimeText, (100, 612))
        self.display.blit(fullTimeText, (700-fullTimeText.get_width(), 612))


    def displayNameArtist(self):
        trackName = mediumFont.render(f"{self.currentSong.title}", True, (65, 152, 255))
        trackArtist = xsmallFont.render(f"{self.currentSong.artist}", True, (65, 152, 255))
        pygame.draw.rect(self.display, (36, 59, 97, 75), pygame.rect.Rect((95, float((600-100)-(mediumFont.get_height()))), (610, 100)))
        self.display.blit(trackName, (100, (600-100)-(mediumFont.get_height())))
        self.display.blit(trackArtist, (100, (600-75)-(xsmallFont.get_height())))

    def displayInfo(self):
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
                icon = "volumeMuted6"
            else:
                icon = "volume6"
        image = pygame.image.load(self.getExecDir() + "images/" + icon + ".png")
        if 30 >= self.volumeTimer > 0:
            image.set_alpha(255-(255/self.volumeTimer))
        elif self.volumeTimer > 30:
            image.set_alpha(255)
        else:
            image.set_alpha(-255)
        temp1, temp2 = image.get_size()
        image = pygame.transform.scale(image, (temp1/1.25, temp2/1.25))
        self.display.blit(image, (800-image.get_width()-8, 800-image.get_height()-8))
        # timeline
        self.displayTimeline()
        # track name and artist
        self.displayNameArtist()

mixer.init()
pygame.font.init()
smallFont = pygame.font.SysFont("monospace", 12)
xsmallFont = pygame.font.SysFont("monospace", 14)
mediumFont = pygame.font.SysFont("monospace", 24, True)
manager = Manager()
manager.getSongs("all")
for arg in argv[1:]:
    if "--help" in arg:
        print(HELP_MENU)
        exit()
    if "--shuffle" in arg:
        manager.shuffleSongs()

manager.startListener()
while DONTQUIT:
    for song in manager.shuffledSongs:
        manager.selectSong()
        while (mixer.music.get_busy() or manager.isPaused) and not manager.songEnd:
            manager.display.fill((0, 0, 0))
            manager.displayCover()
            manager.displayInfo()
            pygame.display.update()
            manager.liveCaption()
            manager.isSongEnd()
            manager.volumeTimer -= 1
            manager.inputTimer -= 1


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

                    if (event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_CTRL):
                        manager.skipNextSong()

                    if event.key == pygame.K_UP:
                        manager.volumeUp()

                    if event.key == pygame.K_DOWN:
                        manager.volumeDown()

                    if event.key == pygame.K_m:
                        manager.volumeMute()

                    if event.key == pygame.K_s:
                        manager.shuffleSongs()