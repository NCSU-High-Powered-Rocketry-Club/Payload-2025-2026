import firm_client

from payload.constants import PORT_LINUX

client = firm_client.FIRMClient(PORT_LINUX)
client.start()

client.reboot()