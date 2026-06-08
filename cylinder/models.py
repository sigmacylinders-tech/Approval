from django.contrib.auth.models import User
from django.db import models

class ApprovalBatch(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"

    project_name = models.CharField(max_length=200)

    project_size = models.CharField(max_length=50)

    cylinder_date = models.DateField()

    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_batches"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    def __str__(self):
        return f"{self.project_name} - {self.cylinder_date}"

class Cylinder(models.Model):
    batch = models.ForeignKey(
        ApprovalBatch,
        on_delete=models.CASCADE,
        related_name="cylinders"
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.serial_number

class ManagerToken(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)