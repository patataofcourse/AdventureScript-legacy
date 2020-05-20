import os
import platform

show = print

def wait():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def query(info, text, choices, allow_save):
    if text != "":
        info.showfunc(text)
    c = 1
    for ch in choices:
        info.showfunc(f"{c}. {ch}")
        c += 1
    result = ""
    while True:
        result = input(">")
        if allow_save:
            if result == "s":
                info.save()
                info.showfunc("Saved!")
                continue
            elif result == "r":
                try:
                    open(f"save/{info.gamename}/{info.save_id}.asv").read().split("}{")
                except:
                    info.showfunc("No save exists!")
                else:
                    info.showfunc("Save restored!")
                    info.reload()
                    return 0
        if result.isdecimal():
            if int(result)-1 in range(len(choices)):
                break
    return result
