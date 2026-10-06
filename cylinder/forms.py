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
            ),
            "project_name": forms.TextInput(
                attrs={
                    "list": "project-names",
                    "autocomplete": "off",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_projects = (
            ApprovalBatch.objects
            .order_by("project_name")
            .values_list("project_name", flat=True)
            .distinct()
        )

    def clean_project_name(self):
        name = self.cleaned_data["project_name"]
        return " ".join(name.split())