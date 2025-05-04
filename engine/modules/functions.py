import os
import random
import string
import pickle
from datetime import datetime
from transliterate import translit, get_available_language_codes

def translitText(text):
    out = translit(text, 'ru', reversed=True)
    return out

def getActualTime():
    return datetime.now()

def generateAdminInviteCode():
    text = [random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase) for i in range(20)]
    code = ''.join(text)
    return code

def getIDWithOffset(call, startPlace):
    idOffset = 0
    for i in range(startPlace, len(call)):
        if (call[i] == "-"):
            break
        idOffset += 1
    id = ""
    if (idOffset != 0):
        for i in range(0, idOffset):
            id += call[startPlace + i]
    else:
        id = call[startPlace]
    return id, idOffset

def deleteFile(path):
    if (os.path.exists(path)):
        os.remove(path)

def getFileContent(path):
    file = open(path)
    content = file.read()
    file.close()
    return content

def writeFileContent(path, data):
    file = open(path, "w")
    file.write(data)
    file.close()

def deleteDirectoryContent(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            pass

def getSystemData():
    file = open("engine/systemData.db", "rb")
    data = pickle.load(file)
    return data