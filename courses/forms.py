from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_name', 'course_code', 'department', 'duration',
            'total_seats', 'available_seats', 'fees', 'eligibility',
            'description', 'status'
        ]
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. BCA'}),
            'course_code': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. BCA'}),
            'department': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. Computer Applications'}),
            'duration': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'e.g. 3 Years'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control-custom'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control-custom'}),
            'fees': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.01'}),
            'eligibility': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control-custom', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select-custom'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_seats')
        available = cleaned_data.get('available_seats')
        if total is not None and available is not None:
            if available > total:
                self.add_error('available_seats', "Available seats cannot exceed total seats.")
        return cleaned_data
