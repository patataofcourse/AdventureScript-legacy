from adventurescript import exceptions

version = "2.0-dev"
save_comp = "1.3.1-dev"

def str_to_ver(ver):
    v = ver
    dev = False
    if ver.endswith("-dev"):
        dev = True
        ver = ver[:-4]
    ver = ver.split(".")
    if len(ver) > 3:
        raise exceptions.SaveVer(ver)
    vnum = []
    for item in ver:
        vnum.append(int(item))
    return vnum + [dev]

def check(ver):
    ver = str_to_ver(ver)
    comp_ver = str_to_ver(save_comp)
    if ver[:3] == comp_ver[:3]:
        return not (ver[3] and (not comp_ver[3]))
    elif ver[:2] == comp_ver[:2]:
        return ver[2] > comp_ver[2]
    elif ver[0] == comp_ver[0]:
        return ver[1] > comp_ver[1]
    else:
        return ver[0] > comp_ver[0]