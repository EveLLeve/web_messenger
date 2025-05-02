from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, SelectMultipleField, widgets
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    """
 A multiple-select, except displays a list of checkboxes.

 Iterating the field will produce subfields, allowing custom rendering of
 the enclosed checkbox fields.
 """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ChatForm(FlaskForm):
    name = StringField('Название чата(не более 50 символов)')
    members = MultiCheckboxField('Добавьте участников')
    photo = FileField('')
    submit = SubmitField('Создать')
