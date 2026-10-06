from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from students.models import StudentProfile

User = get_user_model()

class StudentRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your full name',
            'id': 'reg_full_name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your email address',
            'id': 'reg_email'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your phone number',
            'id': 'reg_phone'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your password',
            'id': 'reg_password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Confirm your password',
            'id': 'reg_confirm_password'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            if len(password) < 6:
                self.add_error('password', "Password must be at least 6 characters long.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.username = self.cleaned_data['email'].split('@')[0]
        
        # Ensure username uniqueness
        base_username = user.username
        counter = 1
        while User.objects.filter(username=user.username).exists():
            user.username = f"{base_username}{counter}"
            counter += 1

        user.role = 'STUDENT'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Initialize empty student profile
            StudentProfile.objects.get_or_create(user=user)
        return user


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your email or username',
            'id': 'login_email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-custom',
            'placeholder': 'Enter your password',
            'id': 'login_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'remember_me'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email_or_user = cleaned_data.get('email', '').strip()
        password = cleaned_data.get('password')

        if email_or_user and password:
            user = authenticate(username=email_or_user, password=password)
            if not user:
                raise ValidationError("Invalid email/username or password.")
            if not user.is_active:
                raise ValidationError("This account has been deactivated. Please contact administration.")
            cleaned_data['user'] = user
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control-custom'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-custom'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control-custom'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-custom'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth', 'gender', 'address', 'city', 'state', 'pincode',
            'father_name', 'mother_name', 'guardian_contact',
            'previous_institution', 'qualification', 'board_university',
            'passing_year', 'percentage_cgpa'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-custom'}),
            'gender': forms.Select(attrs={'class': 'form-select-custom'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control-custom'}),
            'city': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'state': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'guardian_contact': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'previous_institution': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'board_university': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'passing_year': forms.NumberInput(attrs={'class': 'form-control-custom'}),
            'percentage_cgpa': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
        }
