"""Simple pub/sub event bus."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict, List

Listener = Callable[..., None]


class EventBus:
    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[Listener]] = defaultdict(list)

    def subscribe(self, event: str, listener: Listener) -> None:
        self._listeners[event].append(listener)

    def publish(self, event: str, *args, **kwargs) -> None:
        for listener in list(self._listeners.get(event, [])):
            listener(*args, **kwargs)


def get_global_bus() -> EventBus:
    global _GLOBAL_BUS
    try:
        return _GLOBAL_BUS
    except NameError:
        _GLOBAL_BUS = EventBus()
        return _GLOBAL_BUS
