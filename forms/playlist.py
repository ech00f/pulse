from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PlaylistForm(FlaskForm):
    name = StringField("Название плейлиста", validators=[DataRequired(), Length(max=120)])
    is_public = BooleanField("Доступен всем", default=True)
    submit = SubmitField("Создать")
