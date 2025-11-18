from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_password_confirm(self, data, **kwargs):
        password = data.get("password")
        confirm = data.get("confirm_password")
        if confirm and password != confirm:
            raise ValidationError("Passwords must match", field_name="confirm_password")
