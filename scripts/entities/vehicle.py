from mongoengine import Document, StringField, FloatField

class Vehicle(Document):
    vehicle_type = StringField(required=True)
    Brand = StringField(required=True)
    Model = StringField(required=True)
    Engine_type = StringField(required=True)
    mileage = FloatField()
    firebase_uid = StringField(required=True, unique=True)

from scripts.entities.mechanic import Mechanic