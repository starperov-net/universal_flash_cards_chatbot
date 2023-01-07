from collections import deque
from typing import TYPE_CHECKING, AsyncGenerator, Deque, Optional, Type, Any

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Request, Response, TelegramType
from aiogram.types import UNSET, ResponseParameters, User


class MockedSession(BaseSession):
    def __init__(self) -> None:
        super(MockedSession, self).__init__()
        self.responses: Deque[Response[TelegramType]] = deque()  # type: ignore
        self.requests: Deque[Request] = deque()
        self.closed = True

    def add_result(self, response: Response[TelegramType]) -> Response[TelegramType]:
        self.responses.append(response)
        return response

    def get_request(self) -> Request:
        return self.requests.pop()

    async def close(self) -> None:
        self.closed = True

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = UNSET,
    ) -> TelegramType:
        self.closed = False
        self.requests.append(method.build_request(bot))
        response: Response[TelegramType] = self.responses.pop()
        self.check_response(
            method=method, status_code=response.error_code, content=response.json()  # type: ignore
        )
        return response.result  # type: ignore

    async def stream_content(
        self, url: str, timeout: int, chunk_size: int
    ) -> AsyncGenerator[bytes, None]:  # pragma: no cover
        yield b""


class MockedBot(Bot):
    if TYPE_CHECKING:
        session: MockedSession

    def __init__(self, **kwargs: dict[str, str]) -> None:
        super(MockedBot, self).__init__(
            kwargs.pop("token", "42:TEST"), session=MockedSession(), **kwargs  # type: ignore
        )
        self._me = User(
            id=self.id,
            is_bot=True,
            first_name="FirstName",
            last_name="LastName",
            username="tbot",
            language_code="uk-UA",
        )

    def add_result_for(
        self,
        method: Type[TelegramMethod[TelegramType]],
        ok: bool,
        result: Optional[TelegramType] = None,
        description: Optional[str] = None,
        error_code: int = 200,
        migrate_to_chat_id: Optional[int] = None,
        retry_after: Optional[int] = None,
    ) -> Response[TelegramType]:
        response = Response[method.__returning__](  # type: ignore
            ok=ok,
            result=result,
            description=description,
            error_code=error_code,
            parameters=ResponseParameters(
                migrate_to_chat_id=migrate_to_chat_id,
                retry_after=retry_after,
            ),
        )
        self.session.add_result(response)
        return response

    def get_request(self) -> Request:
        return self.session.get_request()
