from sanic import Blueprint
from sanic.response import json

from models.user import User

from sanic_dantic import parse_params, BaseModel

bp_admin = Blueprint("bp_user", url_prefix="/admin")

class UserDTOCreate(BaseModel):
    username: str
    password: str

@bp_admin.post("/users")
@parse_params(body=UserDTOCreate)
async def create_user(_, params: UserDTOCreate):
    user = await User.create(username = params.username, password = params.password)
    return json(user.to_dict())

@bp_admin.get("/users/<id>")
async def get_user(_, id: int):
    user = await User.get_or_404(id)
    return json(user.to_dict())
