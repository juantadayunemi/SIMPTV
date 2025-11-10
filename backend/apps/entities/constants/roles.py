"""
ROLES CONSTANTS
Auto-generated from TypeScript types
"""


class USER_ROLES:
    """Constants from TypeScript USER_ROLES"""

    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


USER_ROLES_CHOICES = (
    ("ADMIN", "Admin"),
    ("OPERATOR", "Operator"),
    ("VIEWER", "Viewer"),
)


class PERMISSIONS:
    """Constants from TypeScript PERMISSIONS"""

    TRAFFIC_CREATE = "traffic:create"
    TRAFFIC_READ = "traffic:read"
    TRAFFIC_UPDATE = "traffic:update"
    TRAFFIC_DELETE = "traffic:delete"
    PLATE_CREATE = "plate:create"
    PLATE_READ = "plate:read"
    PLATE_UPDATE = "plate:update"
    PLATE_DELETE = "plate:delete"
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    SYSTEM_ADMIN = "system:admin"
    SETTINGS_MANAGE = "settings:manage"
    NOTIFICATIONS_MANAGE = "notifications:manage"


PERMISSIONS_CHOICES = (
    ("traffic:create", "Traffic Create"),
    ("traffic:read", "Traffic Read"),
    ("traffic:update", "Traffic Update"),
    ("traffic:delete", "Traffic Delete"),
    ("plate:create", "Plate Create"),
    ("plate:read", "Plate Read"),
    ("plate:update", "Plate Update"),
    ("plate:delete", "Plate Delete"),
    ("user:create", "User Create"),
    ("user:read", "User Read"),
    ("user:update", "User Update"),
    ("user:delete", "User Delete"),
    ("system:admin", "System Admin"),
    ("settings:manage", "Settings Manage"),
    ("notifications:manage", "Notifications Manage"),
)

# Role Permissions Mapping (from TypeScript ROLE_PERMISSIONS)
ROLE_PERMISSIONS = {
    USER_ROLES.ADMIN: [
        PERMISSIONS.TRAFFIC_CREATE,
        PERMISSIONS.TRAFFIC_READ,
        PERMISSIONS.TRAFFIC_UPDATE,
        PERMISSIONS.TRAFFIC_DELETE,
        PERMISSIONS.PLATE_CREATE,
        PERMISSIONS.PLATE_READ,
        PERMISSIONS.PLATE_UPDATE,
        PERMISSIONS.PLATE_DELETE,
        PERMISSIONS.USER_CREATE,
        PERMISSIONS.USER_READ,
        PERMISSIONS.USER_UPDATE,
        PERMISSIONS.USER_DELETE,
        PERMISSIONS.SYSTEM_ADMIN,
        PERMISSIONS.SETTINGS_MANAGE,
        PERMISSIONS.NOTIFICATIONS_MANAGE,
    ],
    USER_ROLES.OPERATOR: [
        PERMISSIONS.TRAFFIC_CREATE,
        PERMISSIONS.TRAFFIC_READ,
        PERMISSIONS.TRAFFIC_UPDATE,
        PERMISSIONS.PLATE_CREATE,
        PERMISSIONS.PLATE_READ,
        PERMISSIONS.PLATE_UPDATE,
        PERMISSIONS.USER_READ,
        PERMISSIONS.NOTIFICATIONS_MANAGE,
    ],
    USER_ROLES.VIEWER: [
        PERMISSIONS.TRAFFIC_READ,
        PERMISSIONS.PLATE_READ,
        PERMISSIONS.USER_READ,
    ],
}
