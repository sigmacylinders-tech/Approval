from django.contrib import admin
from .models import ApprovalBatch, Cylinder, ManagerToken

admin.site.register(ApprovalBatch)
admin.site.register(Cylinder)
admin.site.register(ManagerToken)