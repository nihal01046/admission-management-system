from django import forms
from .models import AdmissionApplication
from courses.models import Course

class ApplicationStep1Form(forms.ModelForm):
    """Step 1: Personal Details"""
    class Meta:
        model = AdmissionApplication
        fields = [
            'full_name', 'email', 'phone_number', 'date_of_birth',
            'gender', 'address', 'father_name', 'mother_name', 'guardian_contact'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-custom', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-custom'}),
            'gender': forms.Select(choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], attrs={'class': 'form-select-custom'}),
            'address': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 2, 'placeholder': 'Address'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': "Father's Name"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': "Mother's Name"}),
            'guardian_contact': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Guardian Contact'}),
        }


class ApplicationStep2Form(forms.ModelForm):
    """Step 2: Academic Details"""
    class Meta:
        model = AdmissionApplication
        fields = [
            'previous_institution', 'qualification', 'board_university',
            'passing_year', 'percentage_cgpa'
        ]
        widgets = {
            'previous_institution': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Previous School / College'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. 12th Standard / Diploma'}),
            'board_university': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. CBSE / State Board'}),
            'passing_year': forms.NumberInput(attrs={'class': 'form-control-custom', 'placeholder': 'Passing Year e.g. 2024'}),
            'percentage_cgpa': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01', 'placeholder': 'Percentage / CGPA'}),
        }


class ApplicationStep3Form(forms.ModelForm):
    """Step 3: Course Preference"""
    class Meta:
        model = AdmissionApplication
        fields = ['course']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select-custom', 'id': 'course_select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(status='Active')


class AdminReviewForm(forms.Form):
    """Admin review status update form"""
    action = forms.ChoiceField(
        choices=[
            ('under_review', 'Mark Under Review'),
            ('doc_verify', 'Mark Documents Verified'),
            ('approve', 'Approve Application'),
            ('reject', 'Reject Application'),
        ],
        widget=forms.Select(attrs={'class': 'form-select-custom'})
    )
    admin_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3, 'placeholder': 'Admin notes or remarks'})
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3, 'placeholder': 'Reason for rejection (Required if rejecting)'})
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('rejection_reason')
        if action == 'reject' and not reason:
            self.add_error('rejection_reason', "Please provide a rejection reason so the applicant is informed.")
        return cleaned_data
