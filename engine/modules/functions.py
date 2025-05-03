import os
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
    return content