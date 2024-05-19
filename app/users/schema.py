from marshmallow import Schema, fields


class UserSchema(Schema):
    user_id = fields.Int(required=True)
    first_name = fields.Str()
    username = fields.Str(allow_none=True)


class SessionSchema(Schema):
    session_id = fields.Int()
    chat_id = fields.Int()
    in_progress = fields.Boolean()
    round_number = fields.Int()


class UserSessionSchema(UserSchema, SessionSchema):
    id_ = fields.Int()
    points = fields.Int()
    in_game = fields.Boolean()
    photo = fields.Str()
