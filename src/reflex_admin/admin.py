from typing import Dict, Type

from .core.resource import Resource

class AdminSite:
    def __init__(self):
        self._registry: Dict[str, Resource] = {}

    def register(self, resource: Resource):
        name = resource.model.__tablename__ if hasattr(resource.model, "__tablename__") else resource.__class__.__name__
        self._registry[name] = resource

    def get_resources(self):
        return dict(self._registry)

admin_site = AdminSite()
