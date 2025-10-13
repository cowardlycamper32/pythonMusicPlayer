import pynput.keyboard as keyboard

def on_press(key):
    print(key)
    if str(key) == '<269025045>':
        print("media stop")
    if key == keyboard.Key.media_previous:
        print("media previous")
    if key == keyboard.Key.media_play_pause:
        print("play/pause")
listener = keyboard.Listener(on_press=on_press)
listener.start()
while True:
    temp = 1