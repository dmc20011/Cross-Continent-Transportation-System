from pydantic import BaseModel
from enum import Enum

#for getting user data
class TrackingReq(BaseModel):
    username: str

class TransitMethod(Enum):
    Sea = 1
    Rail = 2
    Truck = 3
    Air = 4

class OrderStatus(Enum):
    Created = 1
    Processing = 2 
    Shipped = 3
    Delivered = 4 
    Cancelled = 5
    
#Tracking item for frontend
class TrackingItem(BaseModel):
    username: str
    orderNumber: str
    parentNumber: str
    orderDate: str
    orderLastUpdate: str
    startLocation: str
    currentLocation: str
    targetLocation: str
    distkm: int
    transportationMethod: TransitMethod
    deliveryEstimateEarly: str
    deliveryEstimateLate: str
    orderStatus: OrderStatus

class CreateOrUpdateTracker(BaseModel):
    username: str
    orderNumber: str
    parentNumber: str
    orderDate: str
    currentLocation: str
    targetLocation: str
    distkm: int
    transporationMethod: TransitMethod
    orderStatus: OrderStatus

class DeleteOrder(BaseModel):
    username: str
    orderNumber: str

class DeleteUser(BaseModel):
    username: str

class Failure(BaseModel):
    fail: str