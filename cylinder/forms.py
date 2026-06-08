from django import forms
from .models import ApprovalBatch


class ApprovalBatchForm(forms.ModelForm):
    cylinder_count = forms.IntegerField(
        min_value=1,
        label="Number of Cylinders"
    )

    class Meta:
        model = ApprovalBatch
        fields = [
            "project_name",
            "project_size",
            "cylinder_date",
        ]
        widgets = {
            "cylinder_date": forms.DateInput(
                attrs={"type": "date"}
            )
        }