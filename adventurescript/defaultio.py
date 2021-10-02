import os
import platform

class DefaultIO:
    def __init__(self, show, wait, query):
        pass

def show(info, text, **kwargs):
    print(text)

def wait(info, **kwargs):
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        raise Exception("Platform not supported: " + platform.system())

def query(info, text, choices, allow_save, **kwargs):
    if text != "":
        info.showfunc(info, text)
    c = 1
    for ch in choices:
        info.showfunc(info, f"{c}. {ch}")
        c += 1
    result = ""
    while True:
        result = input(">")
        if allow_save:
            if result == "s":
                info.save()
                info.showfunc(info, "Saved!")
                continue
            elif result == "r":
                try:
                    info.load_save()
                except Exception as e:
                    info.showfunc(info, "No save exists!")
                else:
                    info.showfunc(info, "Save restored!")
                    info.reload()
                    return 0
        if result == "q":
            info.status = "quit"
            return 0
        elif result.isdecimal():
            if int(result)-1 in range(len(choices)):
                break
    return int(result)

def load_file(game, filename, mode="r", **kwargs):
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
        "save_p": f"{game}/save_p/{filename}.asv" #for future persistent save (achievements)
    }.get(filetype)
    
    try:
        if mode == "r":
            return open(outfile, encoding="utf-8").read()
        else:
            return open(outfile, mode=mode, encoding="utf-8")
    except FileNotFoundError as e:
        if kwargs.get("createdir"):
            dirname = "/".join(outfile.split("/")[:-1])
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            
            if kwargs.get("create"):
                a = open(outfile, "w")
                a.write("{}")
                a.close()
            if mode == "r":
                return open(outfile, encoding="utf-8").read()
            else:
                return open(outfile, mode=mode, encoding="utf-8")
        else:
            raise e