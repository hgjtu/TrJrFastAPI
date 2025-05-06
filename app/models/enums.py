from enum import Enum

class Role(str, Enum):
    ROLE_USER = "ROLE_USER"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_MODERATOR = "ROLE_MODERATOR"

class PostStatus(str, Enum):
    STATUS_NOT_CHECKED = "STATUS_NOT_CHECKED"
    STATUS_VERIFIED = "STATUS_VERIFIED"
    STATUS_DENIED = "STATUS_VERIFIED"

class PostFilter(str, Enum):
    MY_POST = "my-posts"
    MODERATOR = "moderator"

class PostSort(str, Enum):
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    LIKES_ASC = "likes_asc"
    LIKES_DESC = "likes_desc"
    STATUS_ASC = "status_asc"
    STATUS_DESC = "status_desc"
    LATEST = "latest" 