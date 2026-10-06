from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Lower

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

    def save(self, *args, **kwargs):
        self.project_name = " ".join(self.project_name.split())  # trims and collapses spaces
        super().save(*args, **kwargs)
        self.cylinders.update(project_name=self.project_name)  # keep cylinders in sync if renamed

    def __str__(self):
        return f"{self.project_name} - {self.cylinder_date}"

class Cylinder(models.Model):
    batch = models.ForeignKey(ApprovalBatch, on_delete=models.CASCADE, related_name="cylinders")
    project_name = models.CharField(max_length=200, editable=False, null=True)  # copied from batch
    serial_number = models.CharField(max_length=100)  # removed unique=True

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("project_name"), Lower("serial_number"),
                name="unique_serial_per_project",
            )
        ]

    def save(self, *args, **kwargs):
        self.serial_number = self.serial_number.strip()
        self.project_name = self.batch.project_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.serial_number

class ManagerToken(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)