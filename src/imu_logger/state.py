<<<<<<< Updated upstream
"""
Module for the finite state machine that represents which state of flight the rocket is in.
"""

from abc import ABC, abstractmethod
from typing import Self
import time


class State(ABC):
    """    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """:return: The name of the state"""
        return self.__class__.__name__

    @abstractmethod
    def update(self, _, __) -> Self:
        """
        Called every loop iteration.
        """

class StandbyState(State):
    """
    When the rocket is on the launch rail on the ground.
    """

    __slots__ = ()

    def update(self, firm_packet, _) -> State:
        """
        Checks if the rocket has launched, based on our velocity.
        """
        acceleration = (firm_packet.accel_x_meters_per_s2**2 + firm_packet.accel_y_meters_per_s2**2 + firm_packet.accel_z_meters_per_s2**2)**0.5
        if acceleration > 50:
            return MotorBurnState()
        return self


class MotorBurnState(State):
    """
    When the motor is burning and the rocket is accelerating.
    """

    __slots__ = ("launch_time_s")

    def __init__(self):
        super().__init__()
        self.launch_time_s = time.time()

    def update(self, _, __) -> State:
        if time.time() - self.launch_time_s > 1.6: # CHANGE THIS TO BE MORE PRECISE
            return CoastState()
        return self 


class CoastState(State):
    """
    When the motor has burned out and the rocket is coasting to apogee.

    This is the state we actually control the air brakes extension.
    """

    __slots__ = ()

    def update(self, firm_packet, max_altitude) -> State:
        """
        Checks to see if the rocket has reached apogee, indicating the start of free fall.
        """

        if (
            firm_packet.pressure_altitude_meters <= max_altitude * 0.90
        ):
            return FreeFallState()
        return self


class FreeFallState(State):
    """
    When the rocket is falling back to the ground after apogee.
    """

    __slots__ = ()

    def update(self, firm_packet, _) -> State:
        """
        Check if the rocket has landed, based on our altitude and a spike in acceleration.
        """
        acceleration = (firm_packet.accel_x_meters_per_s2**2 + firm_packet.accel_y_meters_per_s2**2 + firm_packet.accel_z_meters_per_s2**2)**0.5

        # If our altitude is around 0, and we have an acceleration spike, we have landed
        if (firm_packet.pressure_altitude_meters <= 15 and acceleration >= 30):
            return LandedState()
        return self


class LandedState(State):
    """
    When the rocket has landed.
    """

    __slots__ = ()

    def update(self, _, __) -> State:
        """
        We use this method to stop the air brakes system after we have hit our log buffer.
        """
        return self
=======
>>>>>>> Stashed changes
