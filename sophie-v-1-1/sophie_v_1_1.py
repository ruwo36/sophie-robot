from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import httplib2

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
import librosa

import requests
import random
import os
import json
import time
from tqdm import tqdm
import smtplib
from email.message import EmailMessage


# API Keys
PIXABAY_API_KEY = "YOUR_API_HERE"
JAMENDO_API_KEY = "YOUR_API_HERE"
JAMENDO_CLIENT_ID = "YOUR_CLIENT_ID"

APP_PASSWORD = "YOUR_KEY_HERE"
SENDER_EMAIL = "SENDER_EMAIL_HERE"
RECEIVER_EMAIL = "RECIVER_EMAIL_HERE"

VIDEO_COUNT = 0
AUDIO_COUNT = 0
PAGE_NUM = 1

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "credentials/client_secrets.json"
CLIENT_TOKEN_FILE = "credentials/token.json"
AUDIO_ID_FILE = "credentials/audio_id.txt"
VIDEOS_ID_FILE = "credentials/images_id.txt"
REPORT_FILE = "credentials/report.json"

THEMBANIL_PATH = "thembanil/thumbnail.jpg"
BUTTON_PATH = "thembanil/subscribe.png"
FONT_PATH = "thembanil/BebasNeue-Regular.ttf"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CHECK = False

MISSING_CLIENT_SECRETS_MESSAGE = "Set your message (optional)"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

# ==================================================================================================================
# Load JSON File
try:
    with open(REPORT_FILE, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    data = {}


def save_to_json(new_data):
    with open(REPORT_FILE, 'w') as the_file:
        json.dump(new_data, the_file)


# Function to read all available results
def get_all_hits(hits, ids_list):
    for hit in hits:
        if hit['id'] not in ids_list:
            correct_result = hit
            video_id = correct_result['id']
            video_tags = correct_result['tags']
            video_small = correct_result['videos']['small']
            video_small_url = video_small['url']
            video_filename = f"video_{video_id}.mp4"

            # Report
            data['VIDEO']['VIDEO_ID'] = video_id
            data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TAGS'] = video_tags

            try:
                video_url_response = requests.get(video_small_url)

                total_steps = 100

                with tqdm(total=total_steps, desc="Downloading",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as progress_bar:
                    with open(video_filename, 'wb') as vf:
                        for i in range(total_steps):
                            vf.write(video_url_response.content)
                            progress_bar.update(1)

                # Report
                data['VIDEO']['VIDEO_STATE'] = "Success"
                print(f"\nSuccess Download Video: {video_filename}")
                save_to_json(data)

                return {
                    'video_id': video_id,
                    'video_tags': video_tags
                }
            except Exception as e:
                error1 = f"Error in downloading video: {e}"
                print(error1)
                data['VIDEO']['ERRORS'][1] = error1
                save_to_json(data)
                return None
        else:
            print("This Video Already Taken!")
            continue
    return None


# Function to download videos from Pixabay
def download_videos(count, page_num=1):
    global data

    query = ('nature and forest', 'flower and spring', 'green garden')

    url = 'https://pixabay.com/api/videos/'
    params = {
        'key': PIXABAY_API_KEY,
        'q': query[count],
        'category': 'nature',
        'per_page': 200,
        'page': page_num,
        'video_type': 'film',
        'safesearch': 'true',
    }
    videos_response = requests.get(url, params=params)
    response_data = videos_response.json()
    number_of_pages = response_data['total'] // 200

    if 'hits' in response_data and len(response_data['hits']) > 0:
        check = True
        take_count = 0

        with open(VIDEOS_ID_FILE, 'r') as video:
            video_ids = video.read().split("\n")

        while check and take_count < 200:
            take_count += 1
            random_hit = random.choice(response_data['hits'])
            video_id = random_hit['id']
            video_tags = random_hit['tags']
            video_small = random_hit['videos']['small']
            video_small_url = video_small['url']
            video_filename = f"video_{video_id}.mp4"

            # Report
            data['VIDEO']['VIDEO_ID'] = video_id
            data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TAGS'] = video_tags

            if str(video_id) not in video_ids:
                check = False
                try:
                    video_url_response = requests.get(video_small_url)

                    total_steps = 100

                    with tqdm(total=total_steps, desc="Downloading",
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as progress_bar:
                        with open(video_filename, 'wb') as vf:
                            for i in range(total_steps):
                                vf.write(video_url_response.content)
                                progress_bar.update(1)

                    # Report
                    data['VIDEO']['VIDEO_STATE'] = "Success"
                    print(f"\nSuccess Download Video: {video_filename}")
                    save_to_json(data)

                    return {
                        'video_id': video_id,
                        'video_tags': video_tags
                    }
                except Exception as e:
                    error1 = f"Error in downloading video: {e}"
                    print(error1)
                    data['VIDEO']['ERRORS'][1] = error1
                    save_to_json(data)
                    return None
            else:
                print("This Video Already Exist!")
                continue

        if take_count >= 200:
            res = get_all_hits(response_data['hits'], video_ids)
            if res is None:
                page_num += 1
                if page_num <= number_of_pages:
                    download_videos(count, page_num)
                else:
                    print("No Results Left With This Query! I Will Try Anthor...")
                    count += 1
                    download_videos(count)
    else:
        error0 = "No videos found."
        print(error0)
        data['VIDEO']['ERRORS'][0] = error0
        save_to_json(data)
        return None


# Function to download music from Jamendo
def download_music(a_count):
    global data
    query = ('calm,relaxing', 'quit,calm')

    base_url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": JAMENDO_CLIENT_ID,
        "tags": query[a_count],
        "limit": 50,
        "format": "json",
        "include": "musicinfo",
        "audioformat": "mp32",
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Error fetching tracks:", response.json())
        return None

    tracks = response.json().get('results')
    if not tracks:
        print("No tracks found for the specified genre.")
        error0 = "No tracks found for the specified genre."
        data['AUDIO']['ERRORS'][0] = error0
        save_to_json(data)
        return

    check = True
    take_count = 0
    while check and take_count < 200:
        take_count += 1
        random_track = random.choice(tracks)
        title = random_track['name']
        audio_license = random_track['license_ccurl']
        tracks_id = random_track['id']
        with open(AUDIO_ID_FILE, 'r') as audio:
            ids = audio.read().split("\n")
            if str(tracks_id) not in ids:
                download_url = random_track['audio']

                # Report
                data['AUDIO']['AUDIO_ID'] = tracks_id
                data['AUDIO']['AUDIO_NAME'] = title
                data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TITLE'] = title
                data['AUDIO']['AUDIO_LICENSE'] = audio_license

                download_response = requests.get(download_url, stream=True)
                if download_response.status_code == 200:
                    audio_file_name = f"audio_{tracks_id}.mp3"
                    with open(audio_file_name, 'wb') as file:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            file.write(chunk)

                    # Report
                    data['AUDIO']['AUDIO_STATE'] = "Success"
                    print(f"\nSuccess Download audio: {audio_file_name}")
                    save_to_json(data)
                    return {
                        'audio_id': tracks_id,
                        'audio_name': title,
                        'audio_license': audio_license
                    }
                else:
                    print("Failed to download the track.")
                    error1 = "Failed to download the track."
                    data['AUDIO']['ERRORS'][1] = error1
                    save_to_json(data)
                    return None
            else:
                print("This Audio Already Exist!")
                continue

    if take_count >= 200:
        a_count += 1
        time.sleep(0.5)
        if a_count < 3:
            download_music(a_count)
        else:
            a_count = 0
            download_music(a_count)


# Main
video_details = download_videos(VIDEO_COUNT, PAGE_NUM)
audio_details = download_music(AUDIO_COUNT)

data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_DESC'] = f'''
Welcome to another peaceful journey with Calm & Green. In this video,
immerse yourself in the soothing sounds of nature paired with calming music,
designed to help you relax and unwind. Enjoy the tranquil visuals of lush forests,
serene gardens, and calming waterscapes as you let go of stress and find inner peace.
Perfect for meditation, studying, sleeping, or simply escaping the chaos of daily life.\n\n

💚 Don't forget to like, comment, and subscribe for more relaxing videos.\n
🔔 Hit the notification bell so you never miss a moment of calm.\n
🌿 Let us know your favorite scene in the comments!\n\n

Audio License:\n
{audio_details['audio_license']}\n
{data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TAGS'].replace(", ", " #")}
'''
data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_PRIVACY_STATUS'] = "public"
save_to_json(data)

# ==================================================================================================================
#### Creat Thumbnail

def draw_text_with_shadow(draw, position, text, font, fill=(255,255,255), shadow_color=(0,0,0,150), offset=3):
    x, y = position
    draw.text((x+offset, y+offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


mood_phrases_short = {
    "contemporarypiano": "Peaceful Piano Vibes",
    "folk": "Gentle Acoustic Tunes",
    "ambient": "Relaxing Ambient Sounds",
    "newage": "Soothing New Age Flow",
    "electronic": "Soft Electronic Chill",
    "house": "Smooth Deep House",
    "christian": "Peaceful Spiritual Mood",
    "corporate": "Calm Focus Energy",
    "filmscore": "Cinematic Serenity",
    "lofi": "Chill Study Beats",
    "smoothjazz": "Evening Jazz Mood",
    "pop": "Light Uplifting Vibes",
    "world": "Global Peaceful Fusion",
    "reggae": "Tropical Reggae Flow",
    "hiphop": "Chill Hip-Hop Vibes",
    "chillout": "Lounge Calm Moments",
    "rap": "Soft Rap Flow",
    "jazz": "Smooth Relaxing Jazz"
}


main_word = data['AUDIO']['GENRES'].upper()
subtitle = mood_phrases_short.get(main_word.lower(), "Relaxing Nature Music")

# Load Images
img = Image.open(THEMBANIL_PATH)
img = img.resize((1280, 720))
draw = ImageDraw.Draw(img)

# Fonts Setup
font_sub = ImageFont.truetype(FONT_PATH, 55)
font_main = ImageFont.truetype(FONT_PATH, 135)

# Postion
x, y = 80, 400

# Subtitle
draw_text_with_shadow(draw, (x+5, y-40), subtitle, font_sub)

# Main Title
draw_text_with_shadow(draw, (x, y), main_word, font_main)

# Button Postion
button_x = x + 5
button_y = y + 140
button_w, button_h = 251, 70

# Button
button = Image.open(BUTTON_PATH).convert("RGBA")
button = button.resize((button_w, button_h))
img.paste(button, (button_x, button_y), button)

# Soft Vignette For Style
vignette = Image.new("L", img.size, 0)
draw_v = ImageDraw.Draw(vignette)
draw_v.ellipse((0, 0, img.width*1.5, img.height*1.5), fill=255)
vignette = vignette.filter(ImageFilter.GaussianBlur(150))
img.putalpha(vignette)

# Save Image
img.convert("RGB").save("thembanil/final_thumbnail.jpg", "JPEG", quality=96)
print("Thumbnail created: final_thumbnail.jpg")

# ==================================================================================================================

#### Create YouTube Video

video_clip_name = f"video_{data['VIDEO']['VIDEO_ID']}.mp4"
audio_clip_name = f"audio_{data['AUDIO']['AUDIO_ID']}.mp3"

video_clip = VideoFileClip(video_clip_name)
audio_clip = AudioFileClip(audio_clip_name)

width, height = video_clip.size
ratio = width / height

video_duration = video_clip.duration
audio_duration = audio_clip.duration

target_duration = 61 * 60

if round(ratio) == 2:
    repeat_count_audio = int(target_duration // audio_duration) + 1
    repeat_count_video = int(target_duration // video_duration) + 1
    
    looped_audio = concatenate_videoclips([audio_clip] * repeat_count_audio).subclip(0, target_duration)
    looped_video = concatenate_videoclips([video_clip] * repeat_count_video).subclip(0, target_duration)
    
    final_clip = looped_video.set_audio(looped_audio)

    final_clip.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac")
    data['VIDEO']['RATIO'] = "original"
else:
    new_audio_clip = audio_clip.set_end(video_clip.duration)
    final_clip = video_clip.set_audio(new_audio_clip)

    final_clip.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac")

# Report
data['YOUTUBE_VIDEO']['CREATE_YOUTUBE_VIDEO'] = 'Success'
save_to_json(data)

# ==================================================================================================================

#### Apend IDs To Text File

def append_id(file_name, file_id, json_data):
    if file_id is None:
        print("ERROR: `file_id` is None!")
        error3 = "ERROR: **file_id** is None!"
        json_data = error3
        save_to_json(json_data)
    else:
        with open(file_name, 'a') as my_file:
            my_file.write(f"{file_id}\n")


append_id(VIDEOS_ID_FILE, data["VIDEO"]["VIDEO_ID"], data["VIDEO"]["VIDEO_APPEND_STATE"])
print("Success append videos id")

append_id(AUDIO_ID_FILE, data["AUDIO"]["AUDIO_ID"], data["AUDIO"]["AUDIO_APPEND_STATE"])
print("Success append audio id")

# ==================================================================================================================

#### Upload Video To YouTube

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage(CLIENT_TOKEN_FILE)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        try:
            credentials.refresh(Request())

            # Update 'token.json' File
            with open(CLIENT_TOKEN_FILE, 'w') as token:
                token.write(credentials.to_json())

        except Exception as e:
            print(f"Refresh Error: {e}")
            print("Start new authentication...")
            credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, file, title, description, category, keywords, privacyStatus):
    global data

    tags = None
    if keywords:
        tags = keywords.split(",")

    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacyStatus
        )
    )

    # Call the APIs videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    global data

    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                    data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_ID'] = response['id']
                    data['YOUTUBE_VIDEO']['UPLOAD_YOUTUBE_VIDEO'] = "True"
                    save_to_json(data)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
                print("A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
            print("A retriable error occurred: %s" % e)

        if error is not None:
            print(error)
            data['YOUTUBE_VIDEO']['ERRORS'][0] = error
            retry += 1
            if retry > MAX_RETRIES:
                finish_attamp = "No longer attempting to retry."
                data['YOUTUBE_VIDEO']['ERRORS'][1] = finish_attamp
                save_to_json(data)
                exit(finish_attamp)

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)
    data['YOUTUBE_VIDEO']['UPLOAD_RETRY'] = retry
    save_to_json(data)

# Main
file = "output_video.mp4"
title = data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TITLE']
description = data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_DESC'] + f", #{data['VIDEO']['RATIO']}"
category = "22"
keywords = data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TAGS']
privacyStatus = VALID_PRIVACY_STATUSES[0]

if not os.path.exists(file):
    exit("Please specify a valid file.")

youtube = get_authenticated_service()
try:
    initialize_upload(youtube, file, title, description, category, keywords, privacyStatus)
except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    data['YOUTUBE_VIDEO']['ERRORS'][2] = "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
    save_to_json(data)

# ==================================================================================================================

#### Send Report

# The time
year = time.localtime()[0]
mon = time.localtime()[1]
day = time.localtime()[2]

# Main information
MESSAGE_SUBJECT = "YouTube v1.1 Report"
MESSAGE_CONTENT = "Hi Sir,\n" \
                  f"This report in [{str(day)}-{str(mon)}-{str(year)}],\n\n" \
                  "**Downloading Details**\n" \
                  f"  Audio:\n" \
                  f"    Audio Name: {data['AUDIO']['AUDIO_NAME']}\n" \
                  f"    Audio ID: {data['AUDIO']['AUDIO_ID']}\n" \
                  f"    Download State: {data['AUDIO']['AUDIO_STATE']}\n" \
                  f"    Audio License: {data['AUDIO']['AUDIO_LICENSE']}\n" \
                  f"    Append Audio ID: {data['AUDIO']['AUDIO_APPEND_STATE']}\n" \
                  f"    Errors:\n" \
                  f"      {data['AUDIO']['ERRORS'][1]}\n" \
                  f"      {data['AUDIO']['ERRORS'][0]}\n\n" \
                  f"  Video:\n" \
                  f"    Video ID: {data['VIDEO']['VIDEO_ID']}\n" \
                  f"    Download State: {data['VIDEO']['VIDEO_STATE']}\n" \
                  f"    Errors:\n" \
                  f"      {data['VIDEO']['ERRORS'][0]}\n" \
                  f"      {data['VIDEO']['ERRORS'][1]}\n" \
                  f"      {data['VIDEO']['ERRORS'][2]}\n\n" \
                  "**Creating Details**\n" \
                  f"  YouTube Video:\n" \
                  f"    Create Video: {data['YOUTUBE_VIDEO']['CREATE_YOUTUBE_VIDEO']}\n" \
                  f"    Upload The Video: {data['YOUTUBE_VIDEO']['UPLOAD_YOUTUBE_VIDEO']}\n" \
                  f"    Upload Retry: {data['YOUTUBE_VIDEO']['UPLOAD_RETRY']}\n" \
                  f"    Errors:\n" \
                  f"      Upload Error: {data['YOUTUBE_VIDEO']['ERRORS'][0]}\n" \
                  f"      Finish Attempting Error: {data['YOUTUBE_VIDEO']['ERRORS'][1]}\n" \
                  f"      HTTP Error: {data['YOUTUBE_VIDEO']['ERRORS'][2]}\n\n" \
                  f"  Video Details\n" \
                  f"    ID: {data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_ID']}\n" \
                  f"    Title: {data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TITLE']}\n" \
                  f"    Description: {data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_DESC']}\n" \
                  f"    Privacy Status: {data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_PRIVACY_STATUS']}\n" \
                  f"    Tags: {data['YOUTUBE_VIDEO']['YOUTUBE_VIDEO_TAGS']}\n\n" \
                  "End Report."


# Create email message server
message = EmailMessage()

# Set message details
message['From'] = SENDER_EMAIL
message['To'] = RECEIVER_EMAIL
message['Subject'] = MESSAGE_SUBJECT
message.set_content(MESSAGE_CONTENT)

# Run server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(SENDER_EMAIL, APP_KEY)
server.send_message(message)

# Shut down server
server.quit()

# Report Reset
report_data_reset = {
  "AUDIO":{
    "AUDIO_NAME": None,
    "AUDIO_ID": None,
    "AUDIO_STATE": "Failed",
    "AUDIO_APPEND_STATE": "Success",
    "ERRORS": ["No Error", "No Error"]
  },
  "VIDEO": {
    "VIDEO_ID": None,
    "VIDEO_STATE": "Failed",
    "VIDEO_APPEND_STATE": "Success",
    "RATIO": "shorts",
    "ERRORS": [
      "No Error",
      "No Error",
      "No Error"
    ]
  },
  "YOUTUBE_VIDEO": {
    "CREATE_YOUTUBE_VIDEO": "Failed",
    "UPLOAD_YOUTUBE_VIDEO": None,
    "UPLOAD_RETRY": 0,
    "ERRORS": ["No Error", "No Error", "No Error"],
    "YOUTUBE_VIDEO_ID": None,
    "YOUTUBE_VIDEO_TITLE": None,
    "YOUTUBE_VIDEO_DESC": None,
    "YOUTUBE_VIDEO_PRIVACY_STATUS": None,
    "YOUTUBE_VIDEO_TAGS": None
  }
}

with open(REPORT_FILE, 'w') as json_file_reset:
    json.dump(report_data_reset, json_file_reset)

