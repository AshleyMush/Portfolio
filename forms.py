from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length, ValidationError, InputRequired
from flask_ckeditor import CKEditorField

class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Name", "class": "contact-form"})

    email = StringField(label='Email', validators=[DataRequired(), Email(message="You seem to be missing @ or .", check_deliverability=True)],
                        render_kw={"placeholder": "Email", "class": "col-6 col-12-medium"})

    subject= StringField(label='Subject', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Subject", "class": "col-12"})

    message = TextAreaField(label='Message', validators=[DataRequired()],
                                     render_kw={"placeholder": "Enter your message here",  "class": "col-12"})

    submit = SubmitField(label='Send Message', render_kw={"class": "btn btn-dark col-12", "id":"contact_submit_btn" })


class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Name", "class": "contact-form"})

    email = StringField(label='Email', validators=[DataRequired(), Email(message="You seem to be missing @ or .", check_deliverability=True)],
                        render_kw={"placeholder": "Email", "class": "col-6 col-12-medium"})

    password = PasswordField(
        label="Password",
        validators=[DataRequired(message="Do not leave this field empty"),
                    Length(min=8, message="Pasword must be 8 characters minimum"), ])

    confirm_password = PasswordField(
        label="Confirm Password",
        validators=[DataRequired(message="Do not leave this field empty"),
                    Length(min=8, message="Pasword must be 8 characters minimum"), ])

    def validate_password(self, password, confirm_password):
        if password.data != self.confirm_password.data:
            raise ValidationError("Passwords must match.")


    submit = SubmitField('Submit')

    # def validate_email(self, email):
    #     email = User.query.filter_by(email=email.data).first()
    #     if email:
    #         raise ValidationError("Email already exists. Please try another one.")





class LoginForm(FlaskForm):
    email = StringField(label='email', validators=[DataRequired(), Email(message="You seem to be missing @ or .", check_deliverability=True), ])

    password = PasswordField(
        label="Password",
        validators=[DataRequired(message="Do not leave this field empty"),Length(min=8, message="Pasword must be 8 characters minimum"), ])

    submit = SubmitField('Submit')

class AddProjectForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Name", "class": "contact-form"})

    homepage_thumbnail = StringField(label='Homepage Thumbnail', validators=[DataRequired(), URL(require_tld=True)],
                                render_kw={"placeholder": "Homepage Thumbnail", "class": "contact-form"})

    img_url = StringField(label='Image URL', validators=[DataRequired(), URL(require_tld=True)],
                                render_kw={"placeholder": "Image URL", "class": "contact-form"})

    video_url = StringField(label='Video URL', validators=[DataRequired(), URL(require_tld=True)],
                                render_kw={"placeholder": "Video URL", "class": "contact-form"})

    category = StringField(label='Category', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Category", "class": "contact-form"})

    tech_used = StringField(label='Tech Used', validators=[DataRequired(), Length(max=64)],
                                render_kw={"placeholder": "Tech Used", "class": "contact-form"})

    project_url = StringField(label='Project URL', validators=[DataRequired(), URL(require_tld=True)],
                                render_kw={"placeholder": "Project URL", "class": "contact-form"})

    description = CKEditorField(label='Description', validators=[DataRequired()])

    submit = SubmitField(label='Add Project', render_kw={"class": "btn btn-dark col-12", "id":"contact_submit_btn" })



