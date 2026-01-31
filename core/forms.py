from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required.')
    registration_type = forms.ChoiceField(
        choices=User.REGISTRATION_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'registration_type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.registration_type = self.cleaned_data['registration_type']
        
        # As requested: "Afterwards user should be able to login as administrator"
        # We set role_id to 1 (Super Admin) and staff/superuser status
        user.role_id = 1
        user.is_staff = True
        user.is_superuser = True
        
        if commit:
            user.save()
        return user
