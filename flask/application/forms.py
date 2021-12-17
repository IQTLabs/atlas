from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from jinja2 import Markup
from jinja2 import escape
from wtforms import HiddenField, StringField, TextAreaField, SubmitField, Field
from wtforms.validators import DataRequired
from wtforms.widgets import html_params, HTMLString


class InlineButtonWidget(object):
    def __init__(self, class_=None):
        self.class_ = class_

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'submit')
        kwargs["class"] = self.class_
        title = kwargs.pop('title', field.description or '')
        params = html_params(title=title, **kwargs)

        html = '<button %s>%s</button>'
        return HTMLString(html % (params, escape(field.label.text)))


class InlineButton(Field):
    widget = InlineButtonWidget()

    def __init__(self, label=None, validators=None, text='Save', **kwargs):
        super(InlineButton, self).__init__(label, validators, **kwargs)
        self.text = text

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''


class DeleteViewForm(FlaskForm):
    view_id = HiddenField(
        'View_ID',
        [DataRequired()]
    )

    delete_field = Markup('<i class="trash alternate icon"></i>Delete Graph')
    submit_delete = SubmitField(delete_field, widget=InlineButtonWidget(class_="ui negative button"))


class ViewForm(FlaskForm):
    """View form."""
    title = StringField(
        'Title',
        [DataRequired()]
    )
    description = TextAreaField(
        'Description',
        [DataRequired()]
    )
    node_label = StringField(
        'Node Label',
        [DataRequired()]
    )
    edge_label = StringField(
        'Edge Label',
        [DataRequired()]
    )

    graph_data = FileField(validators=[FileRequired()])

    submit_field = Markup('<i class="add icon"></i> Create Graph')
    submit = SubmitField(submit_field, widget=InlineButtonWidget(class_="ui primary labeled icon button"))
