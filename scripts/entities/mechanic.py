from mongoengine import Document, StringField, PointField, ListField

class Mechanic(Document):
    name = StringField(required=True)
    Area = StringField(required=True)
    Contact = StringField(required=True)
    Type = StringField(required=True)
    Reviews = ListField(StringField(), default=[])
    location = PointField(required=True)

    