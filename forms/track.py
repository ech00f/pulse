from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import BooleanField, FileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class UploadTrackForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired(), Length(max=200)])
    artist = StringField("Исполнитель", validators=[DataRequired(), Length(max=200)])
    audio = FileField(
        "Аудиофайл",
        validators=[
            FileRequired(message="Выберите файл"),
            FileAllowed(["mp3", "ogg", "wav", "m4a"], "Только mp3, ogg, wav, m4a"),
        ],
    )
    cover = FileField(
        "Обложка (необязательно)",
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp", "gif"])],
    )
    is_public = BooleanField("Доступен всем", default=True)
    submit = SubmitField("Загрузить")
