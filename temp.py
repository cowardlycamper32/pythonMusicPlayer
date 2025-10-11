
time = 119
if time%60 <= 9:
    seconds = "0" + str(time%60)
else:
    seconds = str(time%60)
print(f"{int(time/60)}:{seconds}")