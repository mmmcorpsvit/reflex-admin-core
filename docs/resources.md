# Resources

Create a Resource:

```python
from reflex_admin.core.resource import Resource
from demo.models import User
from demo.schemas import UserCreate, UserUpdate

class UserAdmin(Resource):
    model = User
    list_display = ["id", "email", "name", "active", "created_at"]
    search_fields = ["email", "name"]
    create_schema = UserCreate
    update_schema = UserUpdate
```

Register:

```python
from reflex_admin.admin import admin_site
admin_site.register(UserAdmin())
```
