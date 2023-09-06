import os
import time
from moviepy.editor import VideoFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from videoconverter import resize_video
import pickle
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog

# Configuration
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
AUTO_TITLE_LIST = "auto-titles-list.txt"
TAGS = " #shorts #RocketLeague #viral"
LAST_USES_FILES_LIST = "files.txt"


# Authentification à l'API YouTube
def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


# Télécharger la vidéo sur YouTube
def upload_video(youtube, filename, title = 'Mon clip Rocket League'):
    """Upload a video to youtube"""
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': '#RocketLeague #shorts #clip #RL #YTshorts',
                'tags': ['rocket league', 'clip'],
                'categoryId': '20' # catégorie Jeux vidéo
            },
            'status': {
                'privacyStatus': 'public'
            }
        },
        media_body=MediaFileUpload(filename)
    )
    response = request.execute()
    print(response)


def save_files(files):
    """Save the files in a file"""
    with open(LAST_USES_FILES_LIST, "w") as f:
        for file in files:
            f.write(file + "\n")

def load_files():
    """Return a set of the files already seen"""
    if not os.path.exists(LAST_USES_FILES_LIST):
        return set()
    files = set()
    with open(LAST_USES_FILES_LIST, "r") as f:
        for line in f.readlines():
            files.add(line[:-1])
    return files

# Surveiller le dossier de clips
def monitor_clip_directory(youtube):
    files_already_seen = load_files()
    print(f"Les fichiers déjà vus sont : {files_already_seen}")
    while True:
        time.sleep(15)
        files_now = set(os.listdir(CLIP_DIR))
        #List theses files in a file
        save_files(files_now)
        #Make a set of the new files
        new_files = files_now - files_already_seen
        for file in new_files:
            print(f"New clip detected : {file}")
            handleNewClip(file)
        #Upload the file of the toPost folder
        for file in os.listdir("toPost"):
            print(f"Trying to Uploading {file}...")
            handleToPostClip(youtube, file)
        files_already_seen = files_now

def handleToPostClip(youtube, name):
    valid_upload : bool = False
    video_title = getVideoTitle() + TAGS
    print(f"Uploading {name} as {video_title}...")
    try :
        upload_video(youtube, os.path.join("toPost", name), title=video_title )
        valid_upload = True
    except Exception as e:
        print("Upload failed")
        youtube = get_authenticated_service()
        print("Retrying...")
        trys += 1
    if not valid_upload:
        print("Upload failed, post it manually")
    else:
        print("Upload successful ! Deleting temp file...")
        os.remove(os.path.join("toPost", name))

def handleNewClip(name) :
    """Handle a new clip, resize it, rename it and move it to the toPost folder"""
    filename = resize_video(os.path.join(CLIP_DIR, name))
    #Copy the video to the toPost folder
    os.rename(filename, os.path.join("toPost", name + ".mp4"))
    print("Clip added as '%s' ..." % (name))


import random

def getVideoTitle() -> str:
    """Choisit un titre au hasard depuis un fichier."""
    
    with open(AUTO_TITLE_LIST, 'r', encoding="utf-8") as file:
        # Lire toutes les lignes du fichier dans une liste
        titles = file.readlines()
    
    # Choisir un titre au hasard
    chosen_title = random.choice(titles)
    # Supprimer premier et dernier caractère
    chosen_title = chosen_title[1:-2]
    
    return chosen_title.strip()  # Supprimer les espaces ou sauts de ligne superflus



# Poster la vidéo sur YouTube
if __name__ == '__main__':
    # Poster la vidéo sur YouTube
    #Load from .env file
    load_dotenv()
    CLIP_DIR = os.getenv("CLIP_DIR")
    if not os.path.exists(CLIP_DIR):
        print("The fichier séléctionné n'existe pas, veuillez en choisir un autre.")
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        CLIP_DIR = filedialog.askdirectory()  # Show an "Open" dialog box and return the path to the selected directory
        #Update .env file
        with open(".env", "w") as f:
            f.write(f"CLIP_DIR={CLIP_DIR}\n")  
            f.close()
    print(f"Le fichier séléctionné est : {CLIP_DIR}")






    youtube = None
    try :
        youtube = get_authenticated_service()
    except Exception as e:
        os.remove('token.pickle')
        youtube = get_authenticated_service()
    # In case of crash, still upload the old clip
    if os.path.exists("new_short.mp4"):
        os.rename("new_short.mp4", os.path.join("toPost", "new_short.mp4"))
    monitor_clip_directory(youtube)