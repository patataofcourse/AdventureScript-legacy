import os
import platform

def show(text, **kwargs):
    print(text)

def wait(**kwargs):
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def query(info, text, choices, allow_save, **kwargs):
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
                    open(f"games/{info.gamename}/save/{info.save_id}.asv").read().split("}{")
                except Exception as e:
                    print(e)
                    info.showfunc("No save exists!")
                else:
                    info.showfunc("Save restored!")
                    info.reload()
                    return 0
        if result.isdecimal():
            if int(result)-1 in range(len(choices)):
                break
    return int(result)

def load_file(game, filename, **kwargs):
    if type(game) != str:
        raise TypeError("game must be a string")
    if type(filename) != str:
        raise TypeError("filename must be a string")
    
    filetype = kwargs.get("type")
    if filetype == "": filetype = None 

    if kwargs.get("chapter") != None and kwargs.get("chapter") != "":
        chapter = kwargs.get("chapter") + "/"
    else:
        chapter = ""

    outfile = "games/" + {
        None: f"{game}/{filename}",
        "script": f"{game}/script/{chapter}{filename}.asf",
        "save": f"{game}/save/{filename}.asv",
        "save_p": f"{game}/save/{filename}.p.asv" #for future persistent save (achievements)
    }.get(filetype)

    return open(outfile).read()