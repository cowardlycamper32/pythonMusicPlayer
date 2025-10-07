import pynput

def onPress(key):
    if key == pynput.keyboard.Key.media_play_pause:
        print("PAUSEPLAY")
    elif key == pynput.keyboard.Key.media_next:
        print("NEXTPLAY")
    elif key == pynput.keyboard.Key.media_previous:
        print("PREVIOUSPLAY")

while True:
    listener = pynput.keyboard.Listener(on_press=onPress)
    listener.start()