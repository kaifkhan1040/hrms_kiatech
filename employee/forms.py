from django import forms
from .models import LeaveApplication, LeaveType
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.forms import ModelForm, TextInput, EmailInput, CharField, PasswordInput, ChoiceField, BooleanField, \
    NumberInput, DateInput,Textarea

class LeaveApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leave_type'].widget.attrs.update({'class': 'form-control'})
        # self.fields['start_date'].widget = DatePickerInput(attrs={'class': 'form-control'})
        # self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['reason'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
            'end_date':DateInput(attrs={
                'type': 'date',
                'class': "form-control mb-2",}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date cannot be after end date.")
        return cleaned_data

class LeaveTypeForm(forms.ModelForm):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
     class Meta:
        model = LeaveType
        fields = ['name', 'description',]