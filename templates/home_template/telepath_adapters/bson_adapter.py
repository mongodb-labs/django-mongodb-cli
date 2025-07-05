from bson import ObjectId
from wagtail.telepath import Adapter, register


class ObjectIdAdapter(Adapter):
    js_constructor = "ObjectId"

    def js_args(self, obj):
        return [str(obj)]


register(ObjectId, ObjectIdAdapter)
