from datetime import datetime, timezone

def ahora_utc() -> datetime:
    """Retorna la fecha y hora actual en UTC con información de zona horaria (timezone-aware)."""
    return datetime.now(timezone.utc)
