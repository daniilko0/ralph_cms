from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.user_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("<int:group>/", views.group, name="group"),
    path("groups/create", views.create_group, name="create_group"),
    path("groups/<int:group>/delete", views.delete_group, name="delete_group"),
    path("<int:group>/students", views.students, name="students"),
    path("<int:group>/student/<int:student_id>", views.student, name="student"),
    path(
        "<int:group>/student/<int:student_id>/edit",
        views.edit_student,
        name="edit_student",
    ),
    path(
        "<int:group>/student/<int:student_id>/delete",
        views.delete_student,
        name="delete_student",
    ),
    path("<int:group>/students/create", views.create_student, name="create_student"),
    path("<int:group>/admin/create", views.create_admin, name="create_admin"),
    path("api/auth/<int:group>", api.AuthLinkView.as_view(), name="get_auth_link"),
]
