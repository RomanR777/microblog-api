from marshmallow import Schema, fields


class PostSerializer(Schema):
    user_id = fields.Integer(required=True)
    title = fields.Str(required=True)
    body = fields.Str(required=True)
    tags = fields.List(fields.Str(), required=True)


class PostDetailSerializer(PostSerializer):
    pk = fields.Integer(required=True)


class SigupSchema(Schema):
    email = fields.Email(required=True)
    nickname = fields.Str(required=True)
    password = fields.Str(required=True)


class SiginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
