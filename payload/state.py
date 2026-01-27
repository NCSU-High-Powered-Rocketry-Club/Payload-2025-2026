"""
Module for the finite state machine that represents which state of flight the rocket is in.
"""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from payload.constants import (
    GRAVE_DEPLOY_LENGTH_SECONDS,
    LAUNCH_ALTITUDE_METERS,
    LAUNCH_STATE_LENGTH_SECONDS,
)

if TYPE_CHECKING:
    from payload.context import Context


class State(ABC):
    """
    The abstract base class for a state. Every state must implement these methods.

    After LandedState, Grave and Zombie diverge in which states they go into.
    """

    __slots__ = ("context", "start_time_ns")

    def __init__(self, context: Context) -> None:
        self.context = context

    @property
    def name(self) -> str:
        """:return: The name of the state"""
        return self.__class__.__name__

    @abstractmethod
    def update(self) -> None:
        """
        Called every loop iteration.

        Uses the Payload Context to interact with the hardware and decides when to move to the
        next state.
        """

    @abstractmethod
    def next_state(self) -> None:
        """
        We never expect/want to go back a state e.g. We're never going to go from Coast to Motor
        Burn, so this method just goes to the next state.
        """


class StandbyState(State):
    """
    When the rocket is on the launch rail on the ground.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        Checks if the rocket has launched, based on our altitude.
        """
        # If we go above 200 meters, we have launched. This is a very delayed, but very safe check.
        if (
            self.context.most_recent_firm_data_packet
            and self.context.most_recent_firm_data_packet.est_position_z_meters
            > LAUNCH_ALTITUDE_METERS
        ):
            self.next_state()

    def next_state(self):
        self.context.state = Launched(self.context)


class Launched(State):
    """
    When the rocket has launched and it is in the air.
    """

    __slots__ = ("_start_time",)

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._start_time = time.monotonic()

    def update(self) -> None:
        """
        Check if enough time has elapsed since launch to say we've landed.
        """
        elapsed = time.monotonic() - self._start_time
        if elapsed >= LAUNCH_STATE_LENGTH_SECONDS:
            self.next_state()

    def next_state(self) -> None:
        self.context.state = LandedState(self.context)


class LandedState(State):
    """
    When the rocket has landed. This is where the state machines
    for Grave and Zombie will diverge.
    """

    __slots__ = ("_start_time",)

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        # If this is zombie, we're just going to set a timer to move on to the next state
        if self.context.zombie:
            self._start_time = time.monotonic()

    def update(self) -> None:
        """
        Handles deciding what state to go into based on if this is Grave or Zombie.
        """
        # If this is Grave, immediately go to deploying Zombie
        if self.context.grave:
            self.next_state()
        # If this is Zombie, wait 10 seconds to be deployed
        elif self.context.zombie:
            elapsed = time.monotonic() - self._start_time
            if elapsed >= GRAVE_DEPLOY_LENGTH_SECONDS:
                self.next_state()

    def next_state(self) -> None:
        if self.context.grave:
            self.context.state = DeployZombieState(self.context)
        elif self.context.zombie:
            self.context.state = ZombieDeployedState(self.context)


class DeployZombieState(State):
    """
    When the rocket has deployed the zombie chute.
    """

    __slots__ = ("_deploy_started",)

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._deploy_started = False

    def update(self) -> None:
        """
        Deploys Zombie from the rocket.
        """
        if not self._deploy_started:
            self.context.deploy_zombie()
            self._deploy_started = True

    def next_state(self) -> None:
        # Grave has no next state, so we explicitly do nothing
        pass


class ZombieDeployedState(State):
    """
    When the rocket has deployed the zombie.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        Orients zombie to be standing up properly.
        """
        # TODO: call some method in context that moves the legs and stands zombie up
        # TODO: write code to detect if zombie is oriented correctly and legs are deployed, then go
        #  to next state
        pass

    def next_state(self) -> None:
        self.context.state = ZombieStandingState(self.context)


class ZombieStandingState(State):
    """
    When the rocket has stood the zombie chute up.
    """

    __slots__ = ()

    def update(self) -> None:
        """
        Drills to collect the soil sample.
        """
        # TODO: call some method in context to do the drilling
        # TODO: write code to detect if the soil has been collected
        pass

    def next_state(self) -> None:
        pass


class ZombieSampleCollectedState(State):
    """
    Once a soil sample has been collected and needs to be analyzed.
    """

    __slots__ = ()

    def update(self) -> None:
        # TODO: have this call a method in context to analyze the soil
        pass

    def next_state(self) -> None:
        # Zombie has no next state, so we explicitly do nothing.
        pass
