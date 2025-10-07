from time import sleep
import keyboard as kb
import pygame
import pathlib
from pygame import mixer, RLEACCEL
from sys import argv
import os
import random
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import pygame_gui
import pygame_gui.data
import CustomKeys.Media as MediaKeys
import pynput.keyboard

if os.name == 'linux':
    TEMP_DIR = f"{pathlib.Path.home()}/.temp/"
else:
    TEMP_DIR = f"{pathlib.Path.home()}/.temp/"

if not pathlib.Path(TEMP_DIR).exists():
    os.mkdir(TEMP_DIR)
if not pathlib.Path(TEMP_DIR + "images").exists():
    os.mkdir(TEMP_DIR + "images")

def getExecutableDir():
    out = ""
    temp = __file__
    print(temp)
    help = temp.split("/")
    if len(help) <= 1:
        help = temp.split("\\")
    help.pop(-1)
    print(help)
    for dir in help:
        out += f"{dir}/"
    print(out)
    return out

EXECUTABLE_DIR = getExecutableDir()
pygame.init()
pygame.display.init()
display = pygame.display.set_mode((800, 800))
guiManager = pygame_gui.UIManager((800, 800))

if len(argv[1:]) < 1:
    print("Usage: python main.py <path>")
    exit(1)
def getCoverImage(path):
    try:
        audio = MP3(path)
        cover = audio.get("APIC:Cover")
        open(TEMP_DIR + "images/cover.png", "w+b").write(cover.data)
        image, imageRect = load_image(TEMP_DIR + "images/cover.png")
    except (KeyError, AttributeError):
        image, imageRect = load_image(EXECUTABLE_DIR + "placeholder.png")
    display.blit(pygame.transform.scale(image, display.get_size()), (0,0), display.get_rect())
    #return cover

def getArtist(path):
    try:
        audio = MP3(path, ID3=EasyID3)
        artist = audio.get("artist")
        return artist[0]
    except:
        return ""

def getTrackName(path):
    try:
        audio = MP3(path, ID3=EasyID3)
        trackName = audio.get("title")
        return trackName[0]
    except:
        return path.split("/")[-1]

def getTrackLen(path):
    try:
        audio = MP3(path, ID3=EasyID3)
        trackLen = audio.info.length
        return trackLen*1000
    except:
        print(path)
        return 0


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

def skipNext(calledFrom="InputLoop"):
    if calledFrom == "InputLoop" or (calledFrom == "global" and not (pygame.key.get_focused() or pygame.mouse.get_focused())):
        global queueHeader
        queueHeader += 1
        return
    if calledFrom == "global":
        print("HELLLLLLLLLLLL")

def skipPrevious():
    global queueHeader
    queueHeader -= 1

def onKeyPress(key):
    global isFocused
    if key == pynput.keyboard.Key.media_play_pause:
        myPause("global")
    elif key == pynput.keyboard.Key.media_next:
        skipNext("global")

def myPause(calledFrom="InputLoop"):
    if calledFrom == "global":
        print("Pausing")
    if calledFrom == "InputLoop" or (calledFrom == "global" and not (pygame.key.get_focused() or pygame.mouse.get_focused())):
        global isPaused
        if isPaused:
            mixer.music.unpause()
        else:
            mixer.music.pause()

    isPaused = not isPaused



test_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 400), (400, 400)), text="Test", manager=guiManager)

mixer.init()
queueHeader = 0
seekPointer = 0
doQuit = False
pygame.key.set_repeat()
loop = True
currentVolume = 1.0
clock = pygame.time.Clock()
testVAR = 0
while not doQuit:
    listener = pynput.keyboard.Listener(on_press=onKeyPress)
    listener.start()
    time_delta = clock.tick(60)/1000.0
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
        mixer.music.set_volume(currentVolume)
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

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == test_button:
                        myPause()

                if event.type == pygame.KEYDOWN:
                    print(event.key)
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                    if (event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_CTRL) or event.key == MediaKeys.K_NEXT_TRACK or kb.is_pressed("next track"):
                        try:
                            mixer.music.rewind()
                            mixer.music.set_pos(getTrackLen(songPaths[queueHeader])/1000)
                            print(getTrackLen(songPaths[queueHeader])/1000)
                            print(mixer.music.get_pos()/1000)
                            skipNext()
                            songEnded = True
                        except pygame.error:
                            pass

                    if (event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_CTRL) or event.key == MediaKeys.K_PREVIOUS_TRACK or kb.is_pressed("previous track"):
                        try:
                            if mixer.music.get_pos() > 5000:
                                mixer.music.rewind()
                            else:
                                queueHeader = queueHeader - 1
                                songEnded = True
                        except pygame.error:
                            pass
                    if event.key == pygame.K_SPACE or event.key == pygame.K_p or event.key == MediaKeys.K_PAUSE_PLAY or kb.is_pressed("play/pause media"):
                        myPause()

                    if event.key == pygame.K_DOWN:
                        mixer.music.set_volume(currentVolume-0.1)
                        currentVolume -= 0.1
                        if currentVolume < 0:
                            currentVolume = 0
                        print(currentVolume)
                    if event.key == pygame.K_UP:
                        mixer.music.set_volume(currentVolume+0.1)
                        currentVolume += 0.1
                        print(currentVolume)
                        if currentVolume > 1:

                            currentVolume = 1.0
                guiManager.process_events(event)
            guiManager.update(time_delta)
            guiManager.draw_ui(display)
            pygame.display.update()