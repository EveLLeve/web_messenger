from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, SelectMultipleField, widgets


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ChatForm(FlaskForm):
    name = StringField('Название чата(не более 50 символов)')
    members = MultiCheckboxField('Добавьте участников')
    photo = FileField('')
    submit = SubmitField('Создать')
