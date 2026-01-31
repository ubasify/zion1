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
        
        # Assign standard User role (role_id=4)
        # Only Super Admins should have access to the Admin-Panel module.
        # User accounts are created as standard users and can be promoted by an existing Super Admin.
        user.role_id = 4
        user.is_staff = False
        user.is_superuser = False
        
        if commit:
            user.save()
        return user
