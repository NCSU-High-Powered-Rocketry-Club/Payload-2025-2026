"""
Module for the finite state machine that represents which state of flight the rocket is in.
"""

from abc import ABC, abstractmethod
import time


class State(ABC):
    """    """

    __slots__ = ("start_time_s")

    @property
    def name(self) -> str:
        """:return: The name of the state"""
        return self.__class__.__name__

    @abstractmethod
    def update(self, _, __) -> None:
        """
        Called every loop iteration.
        """

    @abstractmethod
    def next_state(self) -> None:
        """
        We never expect/want to go back a state e.g. We're never going to go from Flight to Motor
        Burn, so this method just goes to the next state.
        """


class StandbyState(State):
    """
    When the rocket is on the launch rail on the ground.
    """

    __slots__ = ()

    def update(self, firm_packet, _) -> None:
        """
        Checks if the rocket has launched, based on our velocity.
        """
        acceleration = (firm_packet.accel_x_meters_per_s2**2 + firm_packet.accel_y_meters_per_s2**2 + firm_packet.accel_z_meters_per_s2**2)**0.5
        if acceleration > 50:
            self.next_state()

    def next_state(self):
        self.context.state = MotorBurnState(self.context)


class MotorBurnState(State):
    """
    When the motor is burning and the rocket is accelerating.
    """

    __slots__ = ()

    def __init__(self):
        super().__init__()
        self.launch_time_s = time.time()

    def update(self, _, __) -> None:
        if time.time() - self.launch_time_s > 1.6: # CHANGE THIS TO BE MORE PRECISE
            self.next_state()

    def next_state(self) -> None:
        self.context.state = CoastState(self.context)


class CoastState(State):
    """
    When the motor has burned out and the rocket is coasting to apogee.

    This is the state we actually control the air brakes extension.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()

    def update(self, firm_packet, max_altitude) -> None:
        """
        Checks to see if the rocket has reached apogee, indicating the start of free fall.
        """

        if (
            firm_packet.pressure_altitude_meters <= max_altitude * 0.90
        ):
            self.next_state()
            return

    def next_state(self) -> None:
        self.context.state = FreeFallState(self.context)


class FreeFallState(State):
    """
    When the rocket is falling back to the ground after apogee.
    """

    __slots__ = ()

    def update(self, firm_packet, _) -> None:
        """
        Check if the rocket has landed, based on our altitude and a spike in acceleration.
        """
        data = self.context.data_processor
        acceleration = (firm_packet.accel_x_meters_per_s2**2 + firm_packet.accel_y_meters_per_s2**2 + firm_packet.accel_z_meters_per_s2**2)**0.5

        # If our altitude is around 0, and we have an acceleration spike, we have landed
        if (firm_packet.pressure_altitude_meters <= 15 and acceleration >= 30):
            self.next_state()


    def next_state(self) -> None:
        self.context.state = LandedState(self.context)


class LandedState(State):
    """
    When the rocket has landed.
    """

    __slots__ = ()

    def update(self, _, __) -> None:
        """
        We use this method to stop the air brakes system after we have hit our log buffer.
        """
    def next_state(self) -> None:
        # Explicitly do nothing, there is no next state
        pass
