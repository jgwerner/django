from .base import SpawnerInterface


class DummySpawner(SpawnerInterface):
    def __init__(self, server):
        self.server = server

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def terminate(self) -> None:
        return None

    def status(self) -> str:
        return self.server.RUNNING
