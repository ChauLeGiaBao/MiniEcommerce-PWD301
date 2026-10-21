import re
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

def valid_phone(form, field):
    phone = re.sub(r"\s+", "", field.data or "")
    if not re.fullmatch(r"(\+84|0)\d{9,10}", phone):
        raise ValidationError("Số điện thoại không hợp lệ.")

class CheckoutForm(FlaskForm):
    fullname = StringField("Họ tên người nhận", validators=[
        DataRequired(message="Vui lòng nhập họ tên."), Length(max=200)
    ])
    address = TextAreaField("Địa chỉ giao hàng", validators=[
        DataRequired(message="Vui lòng nhập địa chỉ."), Length(max=300)
    ])
    phone = StringField("Số điện thoại", filters=[lambda value: re.sub(r"\s+", "", value or "")],
                        validators=[DataRequired(message="Vui lòng nhập số điện thoại."), valid_phone])
    submit = SubmitField("Xác nhận đặt hàng")
