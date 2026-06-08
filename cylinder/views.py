from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ApprovalBatchForm
from .models import Cylinder, ApprovalBatch, ManagerToken


def index(request):
    return render(request, "cylinder/index.html")


def create_approval_batch(request):

    if request.method == "POST":
        form = ApprovalBatchForm(request.POST)

        if form.is_valid():

            request.session["batch_data"] = {
                "project_name": form.cleaned_data["project_name"],
                "project_size": form.cleaned_data["project_size"],
                "cylinder_date": str(
                    form.cleaned_data["cylinder_date"]
                ),
            }

            return render(
                request,
                "cylinder/serial_numbers.html",
                {
                    "count": form.cleaned_data["cylinder_count"]
                },
            )

    else:
        form = ApprovalBatchForm()

    return render(
        request,
        "cylinder/create_batch.html",
        {
            "form": form
        },
    )

def save_approval_batch(request):

    if request.method != "POST":
        return redirect("create_approval_batch")

    batch_data = request.session.get("batch_data")

    if not batch_data:
        return redirect("create_approval_batch")

    batch = ApprovalBatch.objects.create(
        project_name=batch_data["project_name"],
        project_size=batch_data["project_size"],
        cylinder_date=batch_data["cylinder_date"],
    )

    serial_numbers = request.POST.getlist(
        "serial_numbers"
    )

    cylinders = [
        Cylinder(
            batch=batch,
            serial_number=serial.strip()
        )
        for serial in serial_numbers
        if serial.strip()
    ]

    Cylinder.objects.bulk_create(cylinders)

    del request.session["batch_data"]

    return redirect("index")

def batch_list(request):

    selected_date = request.GET.get("date")

    if selected_date:
        batches = ApprovalBatch.objects.filter(
            cylinder_date=selected_date
        )
    else:
        batches = ApprovalBatch.objects.filter(
            cylinder_date=date.today()
        )

    return render(
        request,
        "cylinder/batch_list.html",
        {
            "batches": batches,
            "selected_date": selected_date or date.today()
        }
    )

def sign_batch(request, pk):

    batch = get_object_or_404(ApprovalBatch, pk=pk)

    if request.method == "POST":

        token = request.POST.get("token")

        try:
            token_obj = ManagerToken.objects.get(
                token=token,
            )

            manager = token_obj.manager

        except ManagerToken.DoesNotExist:
            return render(
                request,
                "cylinder/sign_batch.html",
                {
                    "batch": batch,
                    "error": "Invalid token"
                }
            )

        batch.approved_by = manager
        batch.status = "APPROVED"
        batch.save()

        return redirect("batch_list")

    return render(
        request,
        "cylinder/sign_batch.html",
        {"batch": batch}
    )
def search_cylinder(request):

    cylinder = None

    serial_number = request.GET.get(
        "serial_number",
        ""
    ).strip()

    if serial_number:
        cylinder = (
            Cylinder.objects
            .select_related(
                "batch",
                "batch__approved_by"
            )
            .filter(
                serial_number=serial_number
            )
            .first()
        )

    return render(
        request,
        "cylinder/search_cylinder.html",
        {
            "cylinder": cylinder,
            "serial_number": serial_number,
        }
    )