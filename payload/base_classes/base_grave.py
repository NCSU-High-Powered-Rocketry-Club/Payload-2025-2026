from abc import ABC, abstractmethod


class BaseGrave(ABC):
    @abstractmethod
    def start(self) -> None:
        """Starts the FIRM client for fetching data packets."""

    @abstractmethod
    def stop(self) -> None:
        """Stops the FIRM client for fetching data packets."""

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def deploy_zombie(self):
        """Deploys zombie from grave."""

    @abstractmethod
    def get_data_packet(self):
        pass
