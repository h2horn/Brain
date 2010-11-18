from wtforms import Form, TextField

class Profile(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    email = TextField('E-Mail', [validators.Length(min=6, max=35)])
    nickname = TextField('E-Mail', [validators.Length(min=6, max=25)])

