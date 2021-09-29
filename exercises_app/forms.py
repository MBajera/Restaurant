import django.forms as forms
from django.contrib.auth.models import User
import string
from django.core.exceptions import ValidationError
from .models import Restaurant, OpeningHours, Menu, Dish, Note, Table, Reservation, CATEGORY, DAYS, HOURS

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['restaurant', 'user', 'add_date']

class AddRestaurantForm(forms.Form):
    name = forms.CharField(max_length=255, label="Restaurant name:")
    description = forms.CharField(max_length=255, label="Restaurant short description")
    category = forms.ChoiceField(choices=CATEGORY, label="Category")
    monday_from = forms.ChoiceField(choices=HOURS, label="Monday - open from:")
    monday_to = forms.ChoiceField(choices=HOURS, label="Monday - open to:")
    tuesday_from = forms.ChoiceField(choices=HOURS, label="Tuesday - open from:")
    tuesday_to = forms.ChoiceField(choices=HOURS, label="Tuesday - open to:")
    wednesday_from = forms.ChoiceField(choices=HOURS, label="Wednesday - open from:")
    wednesday_to = forms.ChoiceField(choices=HOURS, label="Wednesday - open to:")
    thursday_from = forms.ChoiceField(choices=HOURS, label="Thursday - open from:")
    thursday_to = forms.ChoiceField(choices=HOURS, label="Thursday - open to:")
    friday_from = forms.ChoiceField(choices=HOURS, label="Friday - open from:")
    friday_to = forms.ChoiceField(choices=HOURS, label="Friday - open to:")
    saturday_from = forms.ChoiceField(choices=HOURS, label="Saturday - open from:")
    saturday_to = forms.ChoiceField(choices=HOURS, label="Saturday - open to:")
    sunday_from = forms.ChoiceField(choices=HOURS, label="Sunday - open from:")
    sunday_to = forms.ChoiceField(choices=HOURS, label="Sunday - open to:")

    def clean(self):
        cleaned_data = super().clean()
        if int(cleaned_data["monday_from"]) > int(cleaned_data["monday_to"]):
            raise ValidationError("Monday opening hours are incorrect")
        if int(cleaned_data["tuesday_from"]) > int(cleaned_data["tuesday_to"]):
            raise ValidationError("Tuesday opening hours are incorrect")
        if int(cleaned_data["wednesday_from"]) > int(cleaned_data["wednesday_to"]):
            raise ValidationError("Wednesday opening hours are incorrect")
        if int(cleaned_data["thursday_from"]) > int(cleaned_data["thursday_to"]):
            raise ValidationError("Thursday opening hours are incorrect")
        if int(cleaned_data["friday_from"]) > int(cleaned_data["friday_to"]):
            raise ValidationError("Friday opening hours are incorrect")
        if int(cleaned_data["saturday_from"]) > int(cleaned_data["saturday_to"]):
            raise ValidationError("Saturday opening hours are incorrect")
        if int(cleaned_data["sunday_from"]) > int(cleaned_data["sunday_to"]):
            raise ValidationError("Sunday opening hours are incorrect")


class AddRestaurantMenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        exclude = ["restaurant", "user", "add_date", "mod_date", "authorized"]


class ModifyRestaurantMenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        exclude = ["restaurant", "user", "add_date", "mod_date"]


class AddNewDishForm(forms.ModelForm):
    class Meta:
        model = Dish
        exclude = ["add_date", "mod_date", "user", "menu"]


class AddExistingDishForm(forms.Form):
    dishes = forms.ModelChoiceField(queryset=Dish.objects.none())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["dishes"].queryset = Dish.objects.filter(user=user)


# USER
class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

def login_validator(login):
    users = User.objects.all().values_list("username", flat=True)
    if login in users:
        raise ValidationError("Login already exists")


def password_validator(password):
    num = False
    ss = False
    for dig in password:
        if dig in string.digits:
            num = True
        elif dig in string.punctuation:
            ss = True
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if password.islower():
        raise ValidationError("Password must contain at least 1 uppercase letter")
    if password.isupper():
        raise ValidationError("Password must contain at least 1 lowercase letter")
    if num == False:
        raise ValidationError("Password must contain at least 1 number")
    if ss == False:
        raise ValidationError("Password must contain at least 1 special character")


class AddUserForm(forms.Form):
    login = forms.CharField(validators=[login_validator], label="Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeat password")
    name = forms.CharField(label="Name")
    surname = forms.CharField(label="Surname")
    email = forms.EmailField(label="Email")

    def clean(self):
        cleaned_data = super().clean()
        password_validator(cleaned_data["password"])
        if cleaned_data["password"] != cleaned_data["password2"]:
            raise ValidationError("Passwords don't match.")


