import unittest
from payload.hardware.grave import Grave

class TestGrave(unittest.TestCase):

    def setUp(self):
        self.grave = Grave()

    def test_motor_extension_default(self):
        position = self.grave.get_motor_extension()
        self.assertEqual(position, 0)

    def test_data_packet(self):
        packet = self.grave.get_data_packet()
        self.assertEqual(packet.position, 0)

    def test_deploy_zombie_runs(self):
        # Just verify it doesn't crash
        self.grave.deploy_zombie()

if __name__ == "__main__":
    unittest.main()
