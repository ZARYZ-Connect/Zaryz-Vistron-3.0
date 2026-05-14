from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','role','phone')

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','phone','photo')
