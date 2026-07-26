from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str