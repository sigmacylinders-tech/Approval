from datetime import date

from django.db import IntegrityError, transaction
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ApprovalBatchForm
from .models import Cylinder, ApprovalBatch, ManagerToken


def index(request):
    return render(request, "cylinder/index.html")


def _render_serial_page(request, count, serials=None, errors=None):
    serials = list(serials or [])
    # pad so the template always shows `count` inputs, keeping what was typed
    serials += [""] * (count - len(serials))

    return render(
        request,
        "cylinder/serial_numbers.html",
        {
            "count": count,
            "serials": serials,
            "errors": errors or [],
        },
    )


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
                "cylinder_count": form.cleaned_data["cylinder_count"],
            }

            return _render_serial_page(
                request,
                form.cleaned_data["cylinder_count"],
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

    project_name = batch_data["project_name"]

    serial_numbers = [
        serial.strip()
        for serial in request.POST.getlist("serial_numbers")
    ]
    count = batch_data.get("cylinder_count", len(serial_numbers))
    filled = [serial for serial in serial_numbers if serial]

    errors = []

    if not filled:
        errors.append("Please enter at least one serial number.")

    # 1. duplicates inside what was just typed
    seen = set()
    repeated = set()
    for serial in filled:
        key = serial.lower()
        if key in seen:
            repeated.add(serial)
        seen.add(key)

    if repeated:
        errors.append(
            "Entered more than once: " + ", ".join(sorted(repeated))
        )

    # 2. serials already registered in this project
    existing = list(
        Cylinder.objects
        .annotate(serial_lower=Lower("serial_number"))
        .filter(
            project_name__iexact=project_name,
            serial_lower__in=seen,
        )
        .values_list("serial_number", flat=True)
    )

    if existing:
        errors.append(
            f"Already registered in project {project_name}: "
            + ", ".join(sorted(existing))
        )

    if errors:
        return _render_serial_page(request, count, serial_numbers, errors)

    # 3. create everything together; the DB constraint is the final safety net
    try:
        with transaction.atomic():
            batch = ApprovalBatch.objects.create(
                project_name=project_name,
                project_size=batch_data["project_size"],
                cylinder_date=batch_data["cylinder_date"],
            )

            Cylinder.objects.bulk_create([
                Cylinder(
                    batch=batch,
                    project_name=batch.project_name,  # bulk_create skips save()
                    serial_number=serial,
                )
                for serial in filled
            ])

    except IntegrityError:
        return _render_serial_page(
            request,
            count,
            serial_numbers,
            ["One of these serial numbers was just registered in this "
             "project by someone else. Please check and try again."],
        )

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

    cylinders = []

    serial_number = request.GET.get(
        "serial_number",
        ""
    ).strip()

    if serial_number:
        cylinders = (
            Cylinder.objects
            .select_related(
                "batch",
                "batch__approved_by"
            )
            .filter(
                serial_number__iexact=serial_number
            )
            .order_by("project_name", "-batch__cylinder_date")
        )

    return render(
        request,
        "cylinder/search_cylinder.html",
        {
            "cylinders": cylinders,
            "serial_number": serial_number,
        }
    )