from firm import FIRM

firm = FIRM(port="/dev/ttyACM0", baudrate=921600)
firm2 = FIRM(port="/dev/ttyAMA0", baudrate=921600)
firm.initialize()
firm.zero_out_pressure_altitude()
firm2.initialize()
firm2.zero_out_pressure_altitude()
prev_packet_time = 0
prev_packet_time2 = 0
while True:
    packets = firm.get_data_packets(block=False)
    packets2 = firm2.get_data_packets(block=False)
    if prev_packet_time is not None and packets:
        dt = packets[0].timestamp_seconds - prev_packet_time
        print(f"1: dt: {dt * 1000:.2f} ms", "len packets:", len(packets))
        prev_packet_time = packets[0].timestamp_seconds
    if prev_packet_time is not None and packets2:
        dt2 = packets2[0].timestamp_seconds - prev_packet_time2
        print(f"2: dt: {dt2 * 1000:.2f} ms", "len packets:", len(packets2))
        prev_packet_time2 = packets2[0].timestamp_seconds
    # if packets:
    #     print(packets[0])
    #     prev_packet_time = packets[0].timestamp_seconds