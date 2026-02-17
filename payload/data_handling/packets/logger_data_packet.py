"""
Module for describing the data packet for the logger to log.
"""

import msgspec


class LoggerDataPacket(msgspec.Struct, array_like=True, kw_only=True):
    """
    Represents a collection of all data that the logger can log in a line.

    Not every field will be filled in every packet. The order in which the fields are defined
    determines the order in which they will be logged.
    """

    # Fields derived from ContextDataPacket
    state_letter: str | None

    # Estimated Data Packet Fields
    est_acceleration_x_gs: float | None = None
    est_acceleration_y_gs: float | None = None
    est_acceleration_z_gs: float | None = None
    est_angular_rate_x_rad_per_s: float | None = None
    est_angular_rate_y_rad_per_s: float | None = None
    est_angular_rate_z_rad_per_s: float | None = None
    est_position_x_meters: float | None = None
    est_position_y_meters: float | None = None
    est_position_z_meters: float | None = None
    est_quaternion_w: float | None = None
    est_quaternion_x: float | None = None
    est_quaternion_y: float | None = None
    est_quaternion_z: float | None = None
    est_velocity_x_meters_per_s: float | None = None
    est_velocity_y_meters_per_s: float | None = None
    est_velocity_z_meters_per_s: float | None = None
    magnetic_field_x_microteslas: float | None = None
    magnetic_field_y_microteslas: float | None = None
    magnetic_field_z_microteslas: float | None = None
    pressure_pascals: float | None = None
    raw_acceleration_x_gs: float | None = None
    raw_acceleration_y_gs: float | None = None
    raw_acceleration_z_gs: float | None = None
    raw_angular_rate_x_deg_per_s: float | None = None
    raw_angular_rate_y_deg_per_s: float | None = None
    raw_angular_rate_z_deg_per_s: float | None = None
    temperature_celsius: float | None = None
    timestamp_seconds: float | None = None

    # Grave packets
    position: None = None

    # Zombie packets
    soil_info: None = None
