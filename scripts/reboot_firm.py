import firm_client

from payload.constants import PORT

client = firm_client.FIRMClient(PORT)
client.start()

client.reboot()