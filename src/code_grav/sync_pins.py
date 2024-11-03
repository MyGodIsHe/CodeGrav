from typing import Callable


class SyncPins:
    def __init__(self):
        self.add_handlers: list[Callable[[str, str], None]] = []

    def add_pin(self, pin_name: str, pin_title: str):
        for handler in self.add_handlers:
            handler(pin_name, pin_title)
