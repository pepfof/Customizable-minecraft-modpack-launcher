from .helper import parse_rule_list
from typing import Dict, Any
import platform
import zipfile
import json
import os

def get_natives(data: Dict[str,Any]) -> str:
    """
    Returns the native part from the json data
    """
    if platform.architecture()[0] == "32bit":
        arch_type = "32"
    else:
        arch_type = "64"
    if "natives" in data:
        if platform.system() == 'Windows':
            if "windows" in data["natives"]:
                return data["natives"]["windows"].replace("${arch}",arch_type)
            else:
                return ""
        elif platform.system() == 'Darwin':
            if "osx" in data["natives"]:
                return data["natives"]["osx"].replace("${arch}",arch_type)
            else:
                return ""           
        else:
            if "linux" in data["natives"]:
                return data["natives"]["linux"].replace("${arch}",arch_type)
            else:
                return "" 
    else:
        return ""

def extract_natives_file(filename: str,extract_path: str,extract_data: Dict[str,Any]):
    """
    Unpack natives
    """
    try:
        os.mkdir(extract_path)
    except:
        pass
    zf = zipfile.ZipFile(filename,"r")
    for i in zf.namelist():
        for e in extract_data["exclude"]:
            if i.startswith(e):
                continue
        zf.extract(i,extract_path)

def extract_natives(versionid: str,path: str,extract_path: str):
    """
    Extract natives into the givrn path. For more information look at the documentation.
    """
    with open(os.path.join(path,"versions",versionid,versionid + ".json")) as f:
        data = json.load(f)
    for count, i in enumerate(data["libraries"]):
        #Check, if the rules allow this lib for the current system
        if not parse_rule_list(i,"rules",{}):
            continue
        currentPath = os.path.join(path,"libraries")
        libPath, name, version = i["name"].split(":")
        for l in libPath.split("."):
            currentPath = os.path.join(currentPath,l)
        currentPath = os.path.join(currentPath,name,version)
        native = get_natives(i)
        if native == "":
            continue
        jarFilenameNative = name + "-" + version + "-" + native + ".jar"
        if "extract" in i:
            extract_natives_file(os.path.join(currentPath,jarFilenameNative),extract_path,i["extract"])
