from time import sleep
import pygame
from pygame import mixer
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

def getArtist(path):
    audio = MP3(path, ID3=EasyID3)
    artist = audio.get("artist")
    return artist[0]
def getTrackName(path):
    audio = MP3(path, ID3=EasyID3)
    trackName = audio.get("title")
    return trackName[0]


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
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def getCoverImage(path):
    audio = MP3(path)
    cover = audio.get("APIC:Cover")
    open(TEMP_DIR + "images/cover.png", "w+b").write(cover.data)
    image, imageRect = load_image(TEMP_DIR + "images/cover.png")
    display.blit(pygame.transform.scale(image, display.get_size()), (0,0), display.get_rect())

    return cover
mixer.init()
songPaths = []
print(argv[1])
if argv[1] == "*" or argv[1] == "all":
    for files in os.listdir("./"):
        if files.endswith(".mp3"):
            songPaths.append("./" + files)
else:
    songPaths.append(argv[1])
random.shuffle(songPaths)
for songs in songPaths:
    pygame.display.set_caption(f"{getTrackName(songs)} - {getArtist(songs)}")
    cover = getCoverImage(songs)
    mixer.music.load(songs)
    mixer.music.play()
    isPaused = False
    songEnd = False
    quit = False
    print(f"playing {songs}")
    while mixer.music.get_busy() or not songEnd:
        if quit == True:
            raise SystemExit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if isPaused:
                        print("Playing")
                        mixer.music.unpause()
                        isPaused = False
                    else:
                        print("Paused")
                        mixer.music.pause()
                        isPaused = True
        pygame.display.update()

        if pygame.key.get_pressed()[pygame.K_q]:
            print("quit")
            quit = True


        if mixer.music.get_endevent():
            songEnd = True
        pygame.event.pump()
    mixer.music.pause()
pygame.quit()
os.remove(TEMP_DIR + "images/cover.png")