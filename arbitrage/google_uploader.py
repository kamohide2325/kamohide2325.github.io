"""
ExcelファイルをGoogleスプレッドシートとしてGoogle Driveにアップロードする
初回のみブラウザでGoogleログインが必要（以降は自動）
"""

import subprocess
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
_DIR = Path(__file__).parent


def upload_to_sheets(filepath: str) -> str:
    """ExcelファイルをGoogleスプレッドシートに変換してアップロードし、URLを返す"""
    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)

    file_name = Path(filepath).stem  # 拡張子なしのファイル名
    file_metadata = {
        "name": file_name,
        "mimeType": "application/vnd.google-apps.spreadsheet",
    }
    media = MediaFileUpload(
        filepath,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=True,
    )
    result = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()

    file_id = result.get("id")
    return f"https://docs.google.com/spreadsheets/d/{file_id}/edit"


def _get_credentials() -> Credentials:
    token_path = _DIR / "token.json"
    creds_path = _DIR / "credentials.json"

    if not creds_path.exists():
        raise FileNotFoundError(
            "credentials.json が見つかりません。\n"
            "Google Cloud Console でOAuth認証情報を作成し、\n"
            f"{creds_path} に配置してください。"
        )

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=True)
            print("ブラウザでGoogleにログインして「許可」をクリックしてください。")
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def open_url(url: str):
    """ブラウザでURLを開く（Mac対応）"""
    subprocess.run(["open", url])
