from lib.track import TrackingService
from lib.req_bodies import *
from datetime import datetime
import pytest
import unittest

class TestTrackingService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("uioghb;kasfgz")
        cls.service = TrackingService("localhost", "localhost", "root", "root")

    def test_create(self):
        create = CreateOrUpdateTracker(
            username="alpha",
            orderNumber="ABC",
            parentNumber="123",
            orderDate=datetime.now().strftime("%Y-%m-%d"),
            currentLocation="China",
            targetLocation="US",
            distkm=10000,
            transporationMethod = TransitMethod.Air,
            orderStatus = OrderStatus.Created
        )
        out = self.service.create_tracking_item(create)
        print(out)


if __name__ == "__main__":
    unittest.main()
    