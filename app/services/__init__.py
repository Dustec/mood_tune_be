import base64
from datetime import datetime


def encode_cursor(dt: datetime, pid: str) -> str:
    raw = f"{dt.isoformat()}|{pid}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, str]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    dt_s, pid = raw.split("|", 1)
    return datetime.fromisoformat(dt_s), pid
