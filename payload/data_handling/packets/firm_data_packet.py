class FIRMDataPacket:
    """Represents a data packet received from the FIRM device."""

    timestamp_seconds: float
    """Timestamp of the data packet in seconds."""
    temperature_celsius: float
    """Ambient temperature measured in degrees Celsius."""
    pressure_pascals: float
    """Atmospheric pressure measured in Pascals."""

    raw_acceleration_x_gs: float
    """Raw accelerometer reading for X-axis in Gs."""
    raw_acceleration_y_gs: float
    """Raw accelerometer reading for Y-axis in Gs."""
    raw_acceleration_z_gs: float
    """Raw accelerometer reading for Z-axis in Gs."""

    raw_angular_rate_x_deg_per_s: float
    """Raw gyroscope reading for X-axis in degrees per second."""
    raw_angular_rate_y_deg_per_s: float
    """Raw gyroscope reading for Y-axis in degrees per second."""
    raw_angular_rate_z_deg_per_s: float
    """Raw gyroscope reading for Z-axis in degrees per second."""

    magnetic_field_x_microteslas: float
    """Magnetometer reading for X-axis in micro-Teslas."""
    magnetic_field_y_microteslas: float
    """Magnetometer reading for Y-axis in micro-Teslas."""
    magnetic_field_z_microteslas: float
    """Magnetometer reading for Z-axis in micro-Teslas."""

    est_position_x_meters: float
    """Estimated position along the X-axis in meters."""
    est_position_y_meters: float
    """Estimated position along the Y-axis in meters."""
    est_position_z_meters: float
    """Estimated position along the Z-axis in meters."""

    est_velocity_x_meters_per_s: float
    """Estimated velocity along the X-axis in meters per second."""
    est_velocity_y_meters_per_s: float
    """Estimated velocity along the Y-axis in meters per second."""
    est_velocity_z_meters_per_s: float
    """Estimated velocity along the Z-axis in meters per second."""

    est_acceleration_x_gs: float
    """Estimated acceleration along the X-axis in Gs."""
    est_acceleration_y_gs: float
    """Estimated acceleration along the Y-axis in Gs."""
    est_acceleration_z_gs: float
    """Estimated acceleration along the Z-axis in Gs."""

    est_angular_rate_x_rad_per_s: float
    """Estimated angular rate around the X-axis in radians per second."""
    est_angular_rate_y_rad_per_s: float
    """Estimated angular rate around the Y-axis in radians per second."""
    est_angular_rate_z_rad_per_s: float
    """Estimated angular rate around the Z-axis in radians per second."""

    est_quaternion_w: float
    """Estimated orientation quaternion scalar component (W)."""
    est_quaternion_x: float
    """Estimated orientation quaternion vector component (X)."""
    est_quaternion_y: float
    """Estimated orientation quaternion vector component (Y)."""
    est_quaternion_z: float
    """Estimated orientation quaternion vector component (Z)."""
