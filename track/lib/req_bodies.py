from pydantic import BaseModel
from enum import Enum

#for getting user data
class TrackingReq(BaseModel):
    username: str

class TransitMethod(Enum):
    Sea = 0
    Rail = 1
    Truck = 2
    Air = 3

class OrderStatus(Enum):
    Created = 0
    Processing = 1 
    Shipped = 2 
    Delivered = 3 
    Cancelled = 4
    
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