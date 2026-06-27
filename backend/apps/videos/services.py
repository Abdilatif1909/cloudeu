from __future__ import annotations

from urllib.parse import parse_qs, urlparse


class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> str:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if host in {"youtu.be", "www.youtu.be"}:
            return parsed.path.strip("/")

        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [""])[0]
            if parsed.path.startswith("/embed/") or parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]

        return ""

    @staticmethod
    def thumbnail_url(video_id: str) -> str:
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
