from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    DateField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

from models.project import PROJECT_TYPES


class NullableDateField(DateField):
    """
    WTForms' stock DateField raises "Not a valid date value" for an empty
    submission even when Optional() is attached - the empty string gets
    parsed (and fails) in process_formdata(), which runs before any
    validators, so Optional() never gets a chance to save it. This treats
    a blank submission as "no date" instead of "invalid date".
    """
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = " ".join(valuelist).strip()
            if not date_str:
                self.data = None
                return
        super().process_formdata(valuelist)


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    college = StringField("College / University", validators=[Optional(), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Reset Password")


class ProjectSubmitForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired(), Length(max=200)])
    project_type = SelectField("Project Type", choices=[(t, t) for t in PROJECT_TYPES], validators=[DataRequired()])
    package_id = SelectField("Package", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Requirements / Description", validators=[DataRequired(), Length(min=20)])
    deadline = NullableDateField("Preferred Deadline", validators=[Optional()])
    requirement_file = FileField(
        "Attach Requirement Document (optional)",
        validators=[FileAllowed(
            ["pdf", "doc", "docx", "zip", "png", "jpg", "jpeg", "txt"],
            "Unsupported file type."
        )],
    )
    submit = SubmitField("Submit Project Request")


class AdminNoteForm(FlaskForm):
    note = TextAreaField("Add Note", validators=[DataRequired(), Length(min=2)])
    submit = SubmitField("Add Note")


class UploadCompletedForm(FlaskForm):
    completed_file = FileField(
        "Upload Deliverable",
        validators=[DataRequired(), FileAllowed(
            ["pdf", "doc", "docx", "zip", "rar", "7z", "ppt", "pptx"],
            "Unsupported file type."
        )],
    )
    submit = SubmitField("Upload File")


class ProfileEditForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    college = StringField("College / University", validators=[Optional(), Length(max=150)])
    avatar = FileField("Profile Photo", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only.")])
    submit = SubmitField("Save Changes")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Send Message")
