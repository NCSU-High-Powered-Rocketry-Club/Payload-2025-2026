"""
Module for the finite state machine that represents which state of flight the rocket is in.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from airbrakes.constants import (
    GROUND_ALTITUDE_METERS,
    LANDED_ACCELERATION_METERS_PER_SECOND_SQUARED,
    MAX_ALTITUDE_THRESHOLD,
    MAX_FREE_FALL_SECONDS,
    MAX_VELOCITY_THRESHOLD,
    TAKEOFF_VELOCITY_METERS_PER_SECOND,
    TARGET_APOGEE_METERS,
)
from airbrakes.utils import convert_ns_to_s

if TYPE_CHECKING:
    from airbrakes.context import Context


class State(ABC):
    """
    Abstract Base class for the states of the air brakes system. Each state will have an update
    method that will be called every loop iteration and a next_state method that will be called when
    the state is over.

    For Airbrakes, we will have 5 states:
    1. Standby - when the rocket is on the rail on the ground
    2. Motor Burn - when the motor is burning and the rocket is accelerating
    3. Coast - after the motor has burned out and the rocket is coasting, this is when air brakes
        deployment will be controlled by the bang-bang controller.
    4. Free Fall - when the rocket is falling back to the ground after apogee, this is when the air
        brakes will be retracted.
    5. Landed - when the rocket lands on the ground. After a few seconds in landed state, the
        Airbrakes program will end.
    """

    __slots__ = ("context", "start_time_ns")

    def __init__(self, context: Context) -> None:
        """:param context: The Airbrakes Context managing the state machine."""
        self.context = context
        # At the very beginning of each state, we retract the air brakes
        self.context.retract_airbrakes()
        self.start_time_ns = context.data_processor.current_timestamp

    @property
    def name(self) -> str:
        """:return: The name of the state"""
        return self.__class__.__name__

    @abstractmethod
    def update(self) -> None:
        """
        Called every loop iteration.

        Uses the Airbrakes Context to interact with the hardware and decides when to move to the
        next state.
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

    def update(self) -> None:
        """
        Checks if the rocket has launched, based on our velocity.
        """
        data = self.context.data_processor
        # If the velocity of the rocket is above a threshold, the rocket has launched.
        # if rocket is past 1000 ft --> next state

        self.context.data_processor.zero_out_altitude()

    def next_state(self):
        self.context.state = Launched(self.context)

class Launched(State):
    """
    When the rocket has launched and the motor is burning.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        5 min timer
        """
        pass


    def next_state(self) -> None:
        # After 5 min passed
        pass

class LandedState(State):
    """
    When the rocket has landed.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        Check if the rocket has been landed for a few seconds.
        """
        pass
        

    def next_state(self) -> None:
        # If ISZOMBIE next state ---> deploy zombie
        # Else if next state ---> being deployed
        pass
    
class DeployZombieState(State):
    """
    When the rocket has deployed the zombie chute.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        grave.deploy_zombie()
        """
        pass


    def next_state(self) -> None:
        # End for grave
        pass
    
class ZombieDeployedState(State):
    """
    When the rocket has deployed the zombie.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        Check if zombie deployment is complete.
        if it is complete next state
        """
        pass


    def next_state(self) -> None:
        # zombie stood up
        pass

class LegDeploymentState(State):
    """
    When the rocket has stood the zombie chute up.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        zombie.deploy_legs()
        check orientation
        if not stood up --> try again\
        if stood up --> next state
        """
        pass


    def next_state(self) -> None:
        # zombie stood up
        pass

class ZombieStoodState(State):
    """
    When the rocket has stood the zombie chute up.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        zombie.start_drilling()
        zombie.start_soil_sensor()
        """
        pass


    def next_state(self) -> None:
        # End program
        pass