from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import httplib2

from moviepy.editor import VideoFileClip, AudioFileClip
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


# ============================================
# Download photos and music
# ============================================

# API Keys
PIXABAY_API_KEY = "YOUR_API_HERE"
JAMENDO_API_KEY = "YOUR_API_HERE"
JAMENDO_CLIENT_ID = "YOUR_CLIENT_ID"

APP_PASSWORD = "YOUR_KEY_HERE"
SENDER_EMAIL = "SENDER_EMAIL_HERE"
RECEIVER_EMAIL = "RECIVER_EMAIL_HERE"

IMAGE_COUNT = 0
AUDIO_COUNT_CHECK = 0
AUDIO_COUNT = 0
PAGE_NUM = 1

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "credentials/client_secrets.json"
CLIENT_TOKEN_FILE = "credentials/token.json"
AUDIO_ID_FILE = "credentials/audio_id.txt"
IMAGES_ID_FILE = "credentials/images_id.txt"
REPORT_FILE = "credentials/report.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = "Set your message (optional)"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


# Load JSON File
try:
    with open(REPORT_FILE, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    data = {}


def save_to_json(new_data):
    with open(REPORT_FILE, 'w') as the_file:
        json.dump(new_data, the_file)

# ============================================
# Download photos and music
# ============================================

# Download Music
def download_music(a_count):
    global data
    query = ('calm,relaxing', 'quit,calm')

    base_url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": JAMENDO_CLIENT_ID,
        "tags": query[a_count],
        "limit": 200,
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
    count = 0
    while check and count < 200:
        random_track = random.choice(tracks)
        title = random_track['name']
        audio_license = random_track['license_ccurl']
        tracks_id = random_track['id']
        with open(AUDIO_ID_FILE, 'r') as audio:
            ids = audio.read().split("\n")
            if str(tracks_id) not in ids:
                check = False
                download_url = random_track['audio']

                # Report
                data['AUDIO']['AUDIO_ID'] = tracks_id
                data['AUDIO']['AUDIO_NAME'] = title

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
        if count >= 200:
            a_count += 1
            if a_count > 1:
                a_count -= 1

            time.sleep(0.5)
            download_music(a_count)


# Download Images
def download_images(count, PAGE_NUM=1):
    global data

    url = 'https://pixabay.com/api/'
    query = ('nature and forest', 'flower and spring', 'green garden')

    params = {
        'key': PIXABAY_API_KEY,
        'q': query[count],
        'category': 'nature',
        'per_page': 200,
        'page': PAGE_NUM,
        'image_type': 'photo',
        'orientation': 'horizontal',
        'safesearch': 'true'
    }

    search_images_response = requests.get(url, params=params)
    if search_images_response.status_code == 200:
        response_data = search_images_response.json()
        number_of_pages = response_data['total'] // 200

        if 'hits' in response_data and len(response_data['hits']) > 0:
            check = True
            count = 0
            while check and count < 200:
                count += 1
                random_hit = random.choice(response_data['hits'])
                pixabay_image_id = random_hit['id']
                pixabay_image_tags = random_hit['tags']

                # Report
                data["IMAGE"]["IMAGE_ID"] = pixabay_image_id
                data['VIDEO']['VIDEO_TAGS'] = pixabay_image_tags

                with open(IMAGES_ID_FILE, 'r') as images:
                    img_ids = images.read().split("\n")
                    if str(pixabay_image_id) not in img_ids:
                        check = False
                        image_url = random_hit['largeImageURL']
                        image_filename = f"image_{pixabay_image_id}.jpg"
                        try:
                            image_response = requests.get(image_url)
                            with open(image_filename, 'wb') as f:
                                f.write(image_response.content)
                            print(f"Downloaded: {image_filename}")
                            data["IMAGE"]["IMAGE_STATE"] = "Success"
                            save_to_json(data)
                            return pixabay_image_id
                        except:
                            print("Error in download images!!")
                            error1 = "Error in download images!!"
                            data["IMAGE"]["ERRORS"][1] = error1
                            save_to_json(data)
                            return None
                    else:
                        print("This image already downloaded")
                        continue
                if count >= 200:
                    PAGE_NUM += 1
                    if PAGE_NUM <= number_of_pages:
                        download_images(count, PAGE_NUM)
                    else:
                        print("No Results Left With This Query! I Will Try Anthor...")
                        count += 1
                        download_images(count)
    else:
        print("Error in search images!!")
        error1 = "Error in search images!!"
        data["IMAGE"]["ERRORS"][1] = error1
        save_to_json(data)
        return None


# ============================================
# Create Waveform
# ============================================

# Crop the images to [16:9]
def crop_to_aspect_ratio(img, target_width, target_height):
    img_height, img_width = img.shape[:2]
    img_aspect_ratio = img_width / img_height
    target_aspect_ratio = target_width / target_height

    # Cropping logic
    if img_aspect_ratio > target_aspect_ratio:
        new_width = int(img_height * target_aspect_ratio)
        x_offset = (img_width - new_width) // 2
        img_cropped = img[:, x_offset:x_offset + new_width]
    else:
        new_height = int(img_width / target_aspect_ratio)
        y_offset = (img_height - new_height) // 2
        img_cropped = img[y_offset:y_offset + new_height, :]

    return img_cropped

# Drawing visualizer for audio data
def draw_visualiser(buffer_length, bar_width, data_array, canvas_height, img_bg):
    img = img_bg.copy()
    x_start = 100
    x_end = 1180
    y_offset = 20

    for i in range(buffer_length):
        bar_height = int(data_array[i] * 20)
        hue = int(i * (180.0 / buffer_length))
        color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
        cv2.rectangle(img, (x_start, canvas_height - bar_height - y_offset),
                      (x_start + bar_width, canvas_height - y_offset), color.tolist(), -1)
        x_start += bar_width
        if x_start >= x_end:
            break
    return img

# Main function
def create_waveform(audio_file, background_image):
    # Load audio file
    y, sr = librosa.load(audio_file)
    # Load and crop background image
    img_bg = cv2.imread(background_image)
    img_bg_cropped = crop_to_aspect_ratio(img_bg, 1280, 720)
    img_bg_resized = cv2.resize(img_bg_cropped, (1280, 720))

    # Set analysis parameters
    hop_length = 2048  # Increased to reduce processing
    fft = 2048
    bar_width = 3
    canvas_height = 720

    # Perform Short-Time Fourier Transform (STFT)
    STFT = np.abs(librosa.stft(y, n_fft=fft, hop_length=hop_length))

    # Set video properties
    height, width, layers = img_bg_resized.shape
    duration_in_seconds = librosa.get_duration(y=y, sr=sr)
    total_frames = STFT.shape[1]
    fps = int(total_frames / duration_in_seconds)

    # Video writer
    video = cv2.VideoWriter("output_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    with tqdm(total=total_frames, desc="Creating Video:", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as progress_bar:
        # Process each frame and write directly to the video
        for i in range(total_frames):
            data_array = STFT[:, i]
            frame = draw_visualiser(len(data_array), bar_width, data_array, canvas_height, img_bg_resized)
            video.write(frame)
            progress_bar.update(1)

    video.release()

    # Merge audio with video
    video_clip = VideoFileClip("output_video.mp4")
    audio_clip = AudioFileClip(audio_file)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile("final_output_video.mp4")


# ============================================
# Upload Video
# ============================================


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
                    data['VIDEO']['VIDEO_ID'] = response['id']
                    data['VIDEO']['UPLOAD_VIDEO'] = "True"
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
            data['VIDEO']['ERRORS'][0] = error
            retry += 1
            if retry > MAX_RETRIES:
                finish_attamp = "No longer attempting to retry."
                data['VIDEO']['ERRORS'][1] = finish_attamp
                save_to_json(data)
                exit(finish_attamp)

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)
    data['VIDEO']['UPLOAD_RETRY'] = retry
    save_to_json(data)


def upload_video():
    global data

    file = "final_output_video.mp4"
    title = data['VIDEO']['VIDEO_TITLE']
    description = '''
    🌿 Enjoy Moments of Relaxation with Our Calm Music 🌿\n

    Welcome to our channel, where we offer you the most beautiful pieces of calming music, carefully designed to bring you a peaceful atmosphere and moments of tranquility. Whether you're looking for music for meditation, studying, working, or even deep sleep, these soothing tunes will accompany you and help you unwind from the stresses of daily life.\n\n

    🎶 What Do We Offer?\n

    Relaxing music for stress relief.\n
    Tunes perfect for meditation and yoga.\n
    Background music ideal for studying and focus.\n
    Natural sounds blended to create a calm and peaceful environment.\n\n
    ✨ Benefits of Calm Music:\n

    Calms the nerves and reduces stress.\n
    Improves focus and creativity.\n
    Enhances deep sleep and emotional relaxation.\n\n
    📌 Don't forget to subscribe and turn on notifications so you never miss out on new tracks that help you live in balance and peace.
    '''
    category = "22"
    keywords = data['VIDEO']['VIDEO_TAGS']
    privacyStatus = VALID_PRIVACY_STATUSES[0]

    if not os.path.exists(file):
        exit("Please specify a valid file.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, file, title, description, category, keywords, privacyStatus)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        data['VIDEO']['ERRORS'][2] = "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        save_to_json(data)


# ============================================
# Append IDs
# ============================================


def append_id(file_name, file_id):
    try:
        with open(file_name, 'a') as my_file:
            my_file.write(f"{file_id}\n")
        print("Append Success")
    except:
        print("Append Faild")


# ============================================
# Send Report
# ============================================

def send_report():
    # Report time
    year = time.localtime()[0]
    mon = time.localtime()[1]
    day = time.localtime()[2]

    # Main information
    MESSAGE_SUBJECT = "The Report"
    MESSAGE_CONTENT = "Hi Sir,\n" \
                    f"This report in [{str(day)}-{str(mon)}-{str(year)}],\n\n" \
                    "**Downloading Details**\n" \
                    f"Audio:\n" \
                    f"  Audio Name: {data['AUDIO']['AUDIO_NAME']}\n" \
                    f"  Audio ID: {data['AUDIO']['AUDIO_ID']}\n" \
                    f"  Download State: {data['AUDIO']['AUDIO_STATE']}\n" \
                    f"  Errors:\n" \
                    f"    {data['AUDIO']['ERRORS'][0]}\n\n" \
                    f"Image:\n" \
                    f"  Image ID: {data['IMAGE']['IMAGE_ID']}\n" \
                    f"  Download State: {data['IMAGE']['IMAGE_STATE']}\n" \
                    "  Errors:\n" \
                    f"    {data['IMAGE']['ERRORS'][1]}\n\n" \
                    "**Creating Details**\n" \
                    f"Create Waveform: {data['VIDEO']['WAVEFORM_STATE']}\n" \
                    f"Create Video: {data['VIDEO']['CREATE_VIDEO']}\n\n" \
                    f"Upload The Video: {data['VIDEO']['UPLOAD_VIDEO']}\n" \
                    f"Upload Retry: {data['VIDEO']['UPLOAD_RETRY']}\n" \
                    "Errors:\n" \
                    f"  Upload Error: {data['VIDEO']['ERRORS'][0]}\n" \
                    f"  Finish Attempting Error: {data['VIDEO']['ERRORS'][1]}\n" \
                    f"  HTTP Error: {data['VIDEO']['ERRORS'][2]}\n\n" \
                    f"**Video Details**\n" \
                    f"ID: {data['VIDEO']['VIDEO_ID']}\n" \
                    f"Title: {data['VIDEO']['VIDEO_TITLE']}\n" \
                    f"Description: {data['VIDEO']['VIDEO_DESC']}\n" \
                    f"Privacy Status: {data['VIDEO']['VIDEO_PRIVACY_STATUS']}\n" \
                    f"Tags: {data['VIDEO']['VIDEO_TAGS']}\n\n" \
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
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.send_message(message)

    # Shut down server
    server.quit()

    # Report Reset
    report_data_reset = {
    "AUDIO":{
        "AUDIO_NAME": None,
        "AUDIO_ID": None,
        "AUDIO_STATE": "Failed",
        "ERRORS": [
        "No Error",
        "No Error"
        ]
    },
    "IMAGE": {
        "IMAGE_ID": None,
        "IMAGE_STATE": "Failed",
        "ERRORS": [
        "No Error",
        "No Error"
        ]
    },
    "VIDEO": {
        "WAVEFORM_STATE": "Failed",
        "CREATE_VIDEO": "Failed",
        "UPLOAD_VIDEO": None,
        "UPLOAD_RETRY": 0,
        "ERRORS": ["No Error", "No Error", "No Error"],
        "VIDEO_ID": None,
        "VIDEO_TITLE": None,
        "VIDEO_DESC": None,
        "VIDEO_PRIVACY_STATUS": None,
        "VIDEO_TAGS": None
    }
    }

    with open(REPORT_FILE, 'w') as json_file_reset:
        json.dump(report_data_reset, json_file_reset)


if __name__ == "__main__":
    # Download Music And Images
    download_music(AUDIO_COUNT)
    download_images(IMAGE_COUNT, PAGE_NUM)
    data['VIDEO']['VIDEO_TITLE'] = f"Relax and calm song - {data['AUDIO']['AUDIO_NAME']}"
    data['VIDEO']['VIDEO_PRIVACY_STATUS'] = "public"
    save_to_json(data)

    # Create Waveform
    AUDIO_FILE = f'audio_{data["AUDIO"]["AUDIO_ID"]}.mp3'
    IMAGE_FILE = f'image_{data["IMAGE"]["IMAGE_ID"]}.jpg'
    create_waveform(AUDIO_FILE, IMAGE_FILE)

    # Upload Video
    upload_video()

    # Append Image and Audio IDs
    append_id(AUDIO_ID_FILE, data["AUDIO"]["AUDIO_ID"])
    append_id(IMAGES_ID_FILE, data["IMAGE"]["IMAGE_ID"])
    
    # Send Final Report
    send_report()
