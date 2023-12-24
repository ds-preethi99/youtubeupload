import streamlit as st
from pytube import YouTube
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle


# Function to authenticate and get YouTube service
def authenticate_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle') and os.path.getsize('token.pickle') > 0:
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


# Function to upload video to YouTube
def upload_video_to_youtube(file_path, title, description):
    youtube = authenticate_youtube()

    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags' : 'internalDSEO',
            'categoryId' : '22',
            },
        'status': {
            'privacyStatus': 'unlisted',
        }
    }

    # Execute the API request
    response = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=file_path
    ).execute()

    return response['id']


# Streamlit app
def main():
    st.title("YouTube Video Uploader")

    # File upload
    video_file = st.file_uploader("Choose a video file", type=["mp4", "mov"])

    # Title and description input
    title = st.text_input("Video Title")
    description = st.text_area("Video Description (optional)")


    # Display video details
    if video_file:
        st.subheader("Video Details:")
        st.write(f"File Name: {video_file.name}")
        st.write(f"File Type: {video_file.type}")
        st.write(f"File Size: {video_file.size} bytes")
    upload_message = st.empty()
    # Upload button
    if st.button("Upload to YouTube"):
        if video_file:
            # Save the video locally
            with open(video_file.name, 'wb') as f:
                f.write(video_file.getvalue())

            upload_message.info("Uploading... Please wait.")
            # Upload video to YouTube
            video_id = upload_video_to_youtube(video_file.name, title, description)

            # Display YouTube URL
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            upload_message.success(f"Video uploaded successfully!\nYouTube URL: {youtube_url}")

            # Clean up: Remove the locally saved video file
            # os.remove(video_file.name)
        else:
            st.warning("Please upload a video file first.")

if __name__ == "__main__":
    main()
