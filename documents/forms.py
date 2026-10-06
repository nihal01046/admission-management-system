from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'title', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select-custom'}),
            'title': forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': 'Optional document title or description'}),
            'file': forms.FileInput(attrs={'class': 'form-control-custom'}),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            # 5MB size limit
            if uploaded_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must not exceed 5MB.")
            # Allowed extensions
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.webp']
            ext = uploaded_file.name.lower().split('.')[-1]
            if f".{ext}" not in allowed_extensions:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG formats are allowed.")
        return uploaded_file
