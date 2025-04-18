"""Standalone python script to download arknights assets and upload them to a branch of the current git repository.

Requires python's requests and .NET 6.0 to be already installed.
"""

import os
import subprocess
import shutil
import sys
import tempfile
import zipfile
import requests

import json

# checkout the actual asset branch
subprocess.run(["git", "fetch", "--depth=1", "origin", "cn:cn"], check=True)
subprocess.run(["git", "checkout", "cn"], check=True)

# prepare network config
network_config_url = "https://ak-conf.hypergryph.com/config/prod/official/network_config"
network_config = json.loads(requests.get(network_config_url).json()["content"])
network_urls = network_config["configs"][network_config["funcVer"]]["network"]
version_url = network_urls["hv"].replace("{0}", "Android")
res_version = requests.get(version_url).json()["resVersion"]
assets_url = network_urls["hu"] + "/Android/assets/" + res_version + "/"

# figure out new files
hot_update_list = requests.get(assets_url + "hot_update_list.json").json()
if os.path.isfile("bundles/hot_update_list.json"):
    with open("bundles/hot_update_list.json", encoding="utf-8") as file:
        old_hot_update_list = json.load(file)

    old_hot_update_list_by_name = {i["name"]: i for i in old_hot_update_list["abInfos"]}
    to_update = [i for i in hot_update_list["abInfos"] if old_hot_update_list_by_name[i["name"]]["hash"] != i["hash"]]
else:
    to_update = hot_update_list["abInfos"]

if len(to_update) == 0 and not (len(sys.argv) > 1 and sys.argv[1] == "--force"):
    print("Up to date")
    exit(0)

to_update_grouped_by_pid: dict[str, list[str]] = {}
for i in to_update:
    to_update_grouped_by_pid.setdefault(i.get("pid"), []).append(i["name"])

# download ArknightsStudioCLI
if os.name == "nt":
    url = "https://github.com/aelurum/AssetStudio/releases/download/ak-v1.2.1/ArknightsStudioCLI-net6-Portable.v1.2.1.zip"
    arknights_studio_path = "ArknightsStudioCLI\\ArknightsStudioCLI.exe"
else:
    url = "https://github.com/thesadru/AssetStudio/releases/download/ak-v1.2.1/ArknightsStudioCLI-net6-linux64.v1.2.1.zip"
    arknights_studio_path = "ArknightsStudioCLI/ArknightsStudioCLI"

if not os.path.isfile(arknights_studio_path):
    print("downloading ArknightsStudioCLI")
    with tempfile.TemporaryFile("wb+") as file:
        with requests.get(url, stream=True) as response:
            for chunk in response.iter_content(chunk_size=None):
                file.write(chunk)
        file.seek(0)
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall("ArknightsStudioCLI")

os.chmod(arknights_studio_path, 0o775)

# update in groups to ensure enough space is present
for pid, to_update in to_update_grouped_by_pid.items():
    print(f"\n\nRunning for pid {pid} ({len(to_update)} files)")

    # download all files
    os.makedirs("bundles", exist_ok=True)
    os.makedirs("bundles/tmp", exist_ok=True)
    for name in to_update:
        print("download", name)

        formatted_name = name.replace("/", "_").replace("#", "__").rsplit(".", 1)[0] + ".dat"
        url = assets_url + formatted_name
        zip_file_path = "bundles/tmp/" + formatted_name

        with requests.get(url, stream=True) as response, open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=None):
                file.write(chunk)

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall("bundles/")

        os.remove(zip_file_path)

    # extract all files to an unstructured output
    print("Extracting files")
    unstructured_assets_path = "unstructured_assets"
    assets_path = "assets"
    os.makedirs(unstructured_assets_path, exist_ok=True)
    for root, dirs, files in os.walk("bundles"):
        for file in files:
            path = os.path.join(root, file)
            du = shutil.disk_usage(".")
            print("extract", os.path.relpath(path, "bundles"), f"({du.free / 2**30:.1f}GB/{du.total / 2**30:.1f}GB remaining)")
            command = [
                arknights_studio_path,
                path,
                "-g",
                "containerFull",
                "-t",
                "Sprite,AkPortraitSprite,AudioClip,TextAsset",
                "--log-level",
                "warning",
                "-o",
                os.path.abspath(unstructured_assets_path),
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
            os.remove(path)

    # move (or overwrite if exists) unstrctured files with the actual assets directory
    # this is to counteract the way duplicates and containerFull behaves
    print("Structuring and overwriting files")
    # get all directories with files in them
    for root, dirs, files in os.walk(unstructured_assets_path):
        # when a file is alone in its directory then move it up a directory
        # when a file is in a numbered directory (with #) then also move it up a directory
        if not files:
            continue
        if len(files) == 1 or "#" in root:
            for file in files:
                current_path = os.path.join(root, file)
                desired_relpath = os.path.join(os.path.dirname(os.path.dirname(os.path.relpath(current_path, unstructured_assets_path))), file)
                future_path = os.path.join(assets_path, desired_relpath).lower()

                os.makedirs(os.path.dirname(future_path), exist_ok=True)
                shutil.move(os.path.abspath(current_path), os.path.abspath(future_path))
        else:
            for file in files:
                current_path = os.path.join(root, file)
                future_path = os.path.join(assets_path, os.path.relpath(current_path, unstructured_assets_path).lower())

                os.makedirs(os.path.dirname(future_path), exist_ok=True)
                shutil.move(os.path.abspath(current_path), os.path.abspath(future_path))

    # clean up to ensure enough space is left for other 'pid's
    print("Cleaning up")
    shutil.rmtree("bundles")
    shutil.rmtree(unstructured_assets_path)

    # push segment to git
    print("Pushing to git")
    sys.stdout.flush()
    subprocess.run(["git", "add", "assets"], check=True)
    subprocess.run(["git", "status"], check=True)
    subprocess.run(["git", "commit", "-m", f"update {res_version} part {pid or 'null'}"], check=True)
    subprocess.run(["git", "log", "--oneline"], check=True)
    subprocess.run(["git", "push", "origin", "cn"], check=True)

    # clean up git commits
    sys.stdout.flush()
    print("Cleaning up git")
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    subprocess.run(["git", "checkout", "--detach", sha], check=True)
    subprocess.run(["git", "fetch", "--depth=1", "origin", "cn:cn"], check=True)
    subprocess.run(["git", "checkout", "cn"], check=True)
    subprocess.run(["git", "reflog", "expire", "--expire=now", "--all"], check=True)
    subprocess.run(["git", "gc", "--prune=now"], check=True)

os.makedirs("bundles", exist_ok=True)
with open("bundles/hot_update_list.json", "w", encoding="utf-8") as file:
    json.dump(hot_update_list, file, ensure_ascii=False, indent=4)


# push final file to git
subprocess.run(["git", "add", "bundles"], check=True)
subprocess.run(["git", "commit", "-m", f"update {res_version} part hot_update_list"], check=True)
subprocess.run(["git", "push", "origin", "cn"], check=True)
subprocess.run(["git", "checkout", "master"], check=True)
