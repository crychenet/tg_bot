import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Awaitable, Callable, Dict

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Any, data: Dict[str, Any]) -> Any:
        if isinstance(event, Message):
            logger.info(f"Входящее сообщение от {event.from_user.full_name} (@{event.from_user.username}): {event.text}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Callback от {event.from_user.full_name} (@{event.from_user.username}): {event.data}")

        return await handler(event, data)
