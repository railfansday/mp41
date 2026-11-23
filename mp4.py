import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file_path, title, description="", category_id="22", privacy_status="private"):
    body = {
        "snippet": {
            "title": title[:100],  # Batas maksimal judul YouTube 100 karakter
            "description": description[:5000],
            "categoryId": category_id,  # 22 = People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,  # "private", "unlisted", atau "public"
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response.get("id")

if __name__ == "__main__":
    if not os.path.exists("keyword.txt"):
        print("❌ keyword.txt tidak ditemukan.")
        exit(1)

    with open("keyword.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    youtube = get_youtube_service()

    for kw in keywords:
        nama_aman = "".join(c if c.isalnum() else "_" for c in kw)
        video_path = f"video_{nama_aman}.mp4"

        if not os.path.exists(video_path):
            print(f"⚠️ File tidak ada: {video_path}, dilewati.")
            continue

        judul = f"{kw.title()} Shorts"
        deskripsi = f"Visual compilation for {kw}."

        try:
            video_id = upload_video(
                youtube=youtube,
                file_path=video_path,
                title=judul,
                description=deskripsi,
                privacy_status="private",  # Ubah ke "public" jika sudah yakin
            )
            print(f"✅ Terunggah: {judul} (ID: {video_id})")
            os.remove(video_path)  # Bersihkan MP4 setelah diunggah
        except Exception as e:
            print(f"❌ Gagal upload {video_path}: {e}")
