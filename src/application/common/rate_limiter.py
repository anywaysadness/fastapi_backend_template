from typing import Protocol


class RateLimiter(Protocol):
    """Порт ограничения частоты операций."""

    async def allow(
        self,
        *,
        scope: str,
        identity: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Учитывает попытку и сообщает, не превышен ли лимит."""
        ...
