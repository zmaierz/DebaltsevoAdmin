import os
import shutil
import platform
from transliterate import translit, get_available_language_codes

def translitText(text):
    out = translit(text, 'ru', reversed=True)
    return out

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