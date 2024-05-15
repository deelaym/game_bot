from marshmallow import Schema, fields


class FileIdSchema(Schema):
    file_id = fields.Str(required=True)


class PhotoListSchema(Schema):
    photos = fields.Nested(FileIdSchema, many=True)
