import os
import urllib.request
import tarfile
import zipfile
import shutil
import tempfile


def fetch_tgz(filename, url, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    filename = os.path.join(downloadDir, filename)
    if not os.path.exists(filename):
        headers = {"Accept": "application/zip"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(filename, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
    with tarfile.open(filename, "r") as file:
        file.extractall(downloadDir)


def fetch_zip(filename, url, dir):
    downloadDir = dir if dir else tempfile.gettempdir()
    filename = os.path.join(downloadDir, filename)
    if not os.path.exists(filename):
        headers = {"Accept": "application/zip"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(filename, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(filename, "r") as file:
        file.extractall(downloadDir)
