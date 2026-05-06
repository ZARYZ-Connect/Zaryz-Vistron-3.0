from django import forms
from django.core.exceptions import ValidationError
from .models import VisitRequest, VisitType
from dashboard.models import Employee, Department
import re


class VisitRequestForm(forms.ModelForm):
    photo = forms.CharField(widget=forms.HiddenInput(), required=False)

    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        required=False,
        empty_label="Select Department"
    )

    class Meta:
        model = VisitRequest
        fields = [
            'full_name', 'email', 'phone',
            'visit_type', 'visit_date',
            'start_time', 'end_time',
            'department', 'whom_to_meet_employee',
            'purpose', 'photo'
        ]

        widgets = {
            'visit_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': True
            }),

            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input time-input',
                'step': '300',
                'required': True
            }),

            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input time-input',
                'step': '300',
                'required': True
            }),

            'purpose': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Brief description of your visit...',
                'style': 'height:70px; resize:vertical;',
                'required': True
            }),

            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your full name',
                'required': True
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your.email@example.com',
                'required': True
            }),

            'phone': forms.TextInput(attrs={
            'class': 'form-input phone-input',
            'maxlength': '10',
            'pattern': '[0-9]{10}',
            'inputmode': 'numeric',
            'required': True
        }),

            'visit_type': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),

            'whom_to_meet_employee': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if not self.organization:
            return

        # 🔐 Filter visit types
        self.fields["visit_type"].queryset = VisitType.objects.filter(
            organization=self.organization
        )
        self.fields["visit_type"].empty_label = "Select Visit Type"
        self.fields["visit_type"].label_from_instance = lambda obj: obj.name

        # 🏢 Filter departments
        self.fields["department"].queryset = Department.objects.filter(
            organization=self.organization
        )
        self.fields["department"].label_from_instance = lambda obj: obj.name

        # Required fields except photo & department
        for name, field in self.fields.items():
            if name not in ("photo", "department"):
                field.required = True
                field.error_messages = {
                    "required": "This field is required."
                }

        # 👤 Department-based employee filtering
        dept_id = None
        if self.is_bound:
            dept_val = self.data.get("department")
            if dept_val and dept_val.isdigit():
                dept_id = int(dept_val)

        if dept_id:
            qs = Employee.objects.filter(
                department_id=dept_id,
                organization=self.organization
            )
        else:
            qs = Employee.objects.filter(
                organization=self.organization
            )

        self.fields["whom_to_meet_employee"].queryset = qs
        self.fields["whom_to_meet_employee"].empty_label = "Select Person to Meet"

        # Pretty labels
        def label_from_instance(obj):
            jr = obj.job_role.name if obj.job_role else ""
            return f"{obj.name} ({jr})" if jr else obj.name

        self.fields["whom_to_meet_employee"].label_from_instance = label_from_instance

    # ----------------------------------------
    # CUSTOM VALIDATIONS
    # ----------------------------------------

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            raise ValidationError("Phone number is required.")

        # Allow only 10 digits
        if not re.fullmatch(r'[0-9]{10}', phone):
            raise ValidationError("Enter a valid 10-digit phone number.")

        return phone

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and end <= start:
            raise ValidationError("End time must be after start time.")

        return cleaned_data
