import abc


class ServerSpawner(object):
    """
    Server service interface to allow start/stop/terminate servers
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server):
        self.server = server

    @abc.abstractmethod
    def start(self, *args, **kwargs) -> None:
        return None

    @abc.abstractmethod
    def stop(self) -> None:
        return None

    @abc.abstractmethod
    def terminate(self) -> None:
        return None

    @abc.abstractmethod
    def status(self) -> str:
        """
        Server statuses should be those defined in server model
        """
        return ''
