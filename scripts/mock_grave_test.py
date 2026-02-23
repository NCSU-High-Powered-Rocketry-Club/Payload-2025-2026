import unittest
from payload.hardware.grave import Grave


class MockServo:
    def release_latch(self):
        print("Mock servo released")


class MockLeadScrew:
    def extend(self, distance):
        print(f"Mock extending {distance} mm")


class TestGrave(unittest.TestCase):

    def test_deploy(self):
        grave = Grave(MockServo(), MockLeadScrew())
        grave.deploy_zombie()


if __name__ == "__main__":
    unittest.main()

# to run, type py -m unittest scripts.run_grave_test in command line