from time import sleep
import pygame
from pygame import mixer, RLEACCEL
from sys import argv
import os
import random
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

TEMP_DIR = "/home/nova/.temp/"

pygame.display.init()
display = pygame.display.set_mode((800, 800))

if len(argv[1:]) < 1:
    print("Usage: python main.py <path>")
    exit(1)
def getCoverImage(path):
    audio = MP3(path)
    cover = audio.get("APIC:Cover")
    open(TEMP_DIR + "images/cover.png", "w+b").write(cover.data)
    image, imageRect = load_image(TEMP_DIR + "images/cover.png")
    display.blit(pygame.transform.scale(image, display.get_size()), (0,0), display.get_rect())
    return cover

def getArtist(path):
    audio = MP3(path, ID3=EasyID3)
    artist = audio.get("artist")
    return artist[0]

def getTrackName(path):
    audio = MP3(path, ID3=EasyID3)
    trackName = audio.get("title")
    return trackName[0]

def getTrackLen(path):
    audio = MP3(path, ID3=EasyID3)
    trackLen = audio.info.length
    return trackLen*1000

def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print(
        '''Cannot load image:''', name)
        raise SystemExit
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()
songPaths = []
if argv[1] == "*" or argv[1] == "all":
    for files in os.listdir("./"):
        if files.endswith(".mp3"):
            songPaths.append("./" + files)
else:
    songPaths.append(argv[1])

def skipNext():
    global queueHeader
    queueHeader += 1

mixer.init()
queueHeader = 0
seekPointer = 0
doQuit = False
pygame.key.set_repeat()
loop = True
while not doQuit:
    if queueHeader > len(songPaths) - 1:
        if loop:
            queueHeader = 0
        else:
            doQuit = True
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    elif queueHeader < 0 and not loop:
        doQuit = True
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    else:
        #print(songPaths)
        #print(queueHeader)
        pygame.display.set_caption(f"{getTrackName(songPaths[queueHeader])} - {getArtist(songPaths[queueHeader])}")
        mixer.music.load(songPaths[queueHeader])
        mixer.music.play()
        songEnded = False
        isPaused = False
        getCoverImage(songPaths[queueHeader])
        pygame.display.update()
        while not songEnded or mixer.get_busy():
            seekPointerTemp = seekPointer
            if seekPointer != seekPointerTemp:
                mixer.music.set_pos(seekPointer)
            seekPointer = mixer.music.get_pos()/1000
            if seekPointer >= getTrackLen(songPaths[queueHeader])/1000 or mixer.music.get_pos() == -1:
                songEnded = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                    if event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        try:
                            mixer.music.rewind()
                            mixer.music.set_pos(getTrackLen(songPaths[queueHeader])/1000)
                            print(getTrackLen(songPaths[queueHeader])/1000)
                            print(mixer.music.get_pos()/1000)
                            skipNext()
                            songEnded = True
                        except pygame.error:
                            pass

                    if event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        try:
                            if mixer.music.get_pos() > 5000:
                                mixer.music.rewind()
                            else:
                                queueHeader = queueHeader - 1
                                songEnded = True
                        except pygame.error:
                            pass
                    if event.key == pygame.K_SPACE or event.key == pygame.K_p:
                        if isPaused:
                            mixer.music.unpause()
                            isPaused = False
                        else:
                            mixer.music.pause()
                            isPaused = True
