from code_grav.space_types import BasePin


class SyncPins:
    def __init__(self):
        self.add_handlers: list = []

    def add_pin(self, pin_name: str):
        for handler in self.add_handlers:
            handler(pin_name)
