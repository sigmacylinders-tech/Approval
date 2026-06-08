from django.urls import path
from . import views

urlpatterns = [

path("", views.index, name="index"),
path(
    "approval-batches/create/",
    views.create_approval_batch,
    name="create_approval_batch",
),

path(
    "approval-batches/save/",
    views.save_approval_batch,
    name="save_approval_batch",
),
path("batches/", views.batch_list, name="batch_list"),
path("batches/<int:pk>/sign/", views.sign_batch, name="sign_batch"),
path(
    "search/",
    views.search_cylinder,
    name="search_cylinder"
),
]