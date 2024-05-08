import shutil
import urllib.request
import zipfile
import os


def download(username, repoName, outputPath, repoBranch="master"):
    filename = os.path.join(outputPath, repoName)
    if os.path.exists(filename):
        return
    if not os.path.exists(filename + ".zip"):
        url = (
            f"https://github.com/{username}/{repoName}/archive/refs/heads/{repoBranch}"
            ".zip"
        )
        headers = {"Accept": "application/zip"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(filename + ".zip", "wb") as out_file:
                shutil.copyfileobj(response, out_file)
    zf = zipfile.ZipFile(filename + ".zip", "r")
    zf.extractall(outputPath)
    os.rename(filename + "-" + repoBranch, filename)
