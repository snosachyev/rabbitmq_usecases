import datetime as dt
import pika
import threading

from abc import ABC, abstractmethod

from functools import cached_property
from typing import Any, Protocol, Union

from pydantic import BaseModel

from core.config import rabbit_params


class BaseSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            dt.date: lambda v: v.isoformat(),
            dt.datetime: lambda v: v.isoformat(),
            Exception: lambda e: str(e),
        }
        allow_mutation = True
        keep_untouched = (cached_property,)


class UseCaseRequest(BaseSchema):
    pass


class UseCaseResponse(BaseSchema):
    status: Any = None


class WorkQueuesResponse(UseCaseResponse):
    status: str = 'received'


class ProducerRequestUseCase(Protocol):
    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        with pika.BlockingConnection(rabbit_params) as connection:
            return self._execute(connection.channel(), request)

    def _execute(self, channel, request: Union[UseCaseRequest, None]) -> Union[UseCaseResponse, None]:
        raise NotImplementedError()


class ProducerUseCase(Protocol):
    def execute(self):
        # Use context manager to automatically close the connection when the process stops.
        with pika.BlockingConnection(rabbit_params) as connection:
            channel = connection.channel()
            return self._execute(channel)

    def _execute(self, channel):
        raise NotImplementedError()


class ConsumerUseCase(ABC):
    def execute(self):
        # Use context manager to automatically close the connection when the process stops.
        with pika.BlockingConnection(rabbit_params) as connection:
            channel = connection.channel()
            self._execute(channel)

    @abstractmethod
    def _execute(self, channel, request: UseCaseRequest) -> UseCaseResponse:
        raise NotImplementedError()

    @abstractmethod
    def _do_work(self, channel, delivery_tag, body, tlock: threading.Lock):
        return NotImplemented
