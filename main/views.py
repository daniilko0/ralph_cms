import os

import requests
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q

from .forms import GroupInfoForm
from .forms import GroupScheduleForm
from .forms import StudentForm
from .forms import VkForm
from .models import Groups
from .models import Schedule
from .models import StudentStatus
from .models import Users
from .models import UsersInfo


def index(request):
    context = {"groups": Groups.objects.all()}
    return render(request, "main/index.html", context)


def students(request, group):
    context = {}
    try:
        group_object = Groups.objects.get(group_num=group)
    except Groups.DoesNotExist:
        raise Http404("Группа не существует.")
    else:
        context["group"] = group_object
        students = UsersInfo.objects.filter(group_num=group).order_by("user_id")
        acad_statuses = StudentStatus.objects.all()
        context["students"] = students
        context["acad_statuses"] = acad_statuses
        return render(request, "main/students.html", context)


def student(request, group, student_id):
    context = {}
    student = UsersInfo.objects.get(user_id=student_id)
    try:
        user = Users.objects.get(id=student_id)
    except Users.DoesNotExist:
        pass
    else:
        context["vk_link"] = f"https://vk.com/id{user.vk_id}"

    acad_status = StudentStatus.objects.get(status_id=student.academic_status.status_id)
    context["group"] = group
    context["student"] = student
    context["acad_status"] = acad_status

    return render(request, "main/student.html", context)


def edit_student(request, student_id, group):
    context = {}
    try:
        student = UsersInfo.objects.get(user_id=student_id)
        user = Users.objects.get(id=student_id)
    except UsersInfo.DoesNotExist:
        raise Http404("Студент не существует.")
    else:
        vk_link = f"https://vk.com/id{user.vk_id}"
        info_form = StudentForm(instance=student)
        vk_form = VkForm(instance=user, initial={"vk_link": vk_link})
        if request.method == "POST":
            info_form = StudentForm(request.POST)
            vk_form = VkForm(request.POST)
            if info_form.is_valid() and vk_form.is_valid():
                UsersInfo.objects.filter(user_id=student_id).update(
                    first_name=request.POST["first_name"],
                    second_name=request.POST["second_name"],
                    group_num=int(request.POST["group_num"]),
                    subgroup_num=int(request.POST["subgroup_num"]),
                    academic_status=int(request.POST["academic_status"]),
                )

                query_url = "https://api.vk.com/method/users.get"
                if request.POST["vk_link"].startswith("https://vk.com/id"):
                    vk_screen_name = request.POST["vk_link"].replace(
                        "https://vk.com/id", ""
                    )
                else:
                    vk_screen_name = request.POST["vk_link"].replace(
                        "https://vk.com/", ""
                    )
                query_params = {
                    "user_ids": vk_screen_name,
                    "access_token": os.environ["VK_USER_TOKEN"],
                    "v": "5.103",
                }

                query = requests.get(query_url, query_params)
                vk_id = query.json()["response"][0]["id"]
                Users.objects.filter(id=student_id).update(vk_id=vk_id)
                return redirect("student", group, student_id)
        context["student"] = student
        context["info_form"] = info_form
        context["vk_form"] = vk_form
        context["group"] = group

        return render(request, "main/student_edit.html", context)


def delete_student(request, group, student_id):
    try:
        student = UsersInfo.objects.get(user_id=student_id)
        user = Users.objects.get(id=student_id)
    except UsersInfo.DoesNotExist:
        raise Http404("Студент не существует.")
    else:
        student.delete()
        user.delete()
        return redirect("students", group)


def create_student(request, group):
    context = {}
    info_form = StudentForm(initial={"group_num": group})
    vk_form = VkForm()
    if request.method == "POST":
        info_form = StudentForm(request.POST)
        vk_form = VkForm(request.POST)
        if info_form.is_valid() and vk_form.is_valid():
            new_student = UsersInfo(
                first_name=request.POST["first_name"],
                second_name=request.POST["second_name"],
                group_num=int(request.POST["group_num"]),
                subgroup_num=int(request.POST["subgroup_num"]),
                academic_status=StudentStatus.objects.get(
                    status_id=int(request.POST["academic_status"])
                ),
            )
            new_student.save()
            new_student_id = new_student.user_id

            query_url = "https://api.vk.com/method/users.get"
            if request.POST["vk_link"].startswith("https://vk.com/id"):
                vk_screen_name = request.POST["vk_link"].replace(
                    "https://vk.com/id", ""
                )
            else:
                vk_screen_name = request.POST["vk_link"].replace("https://vk.com/", "")
            query_params = {
                "user_ids": vk_screen_name,
                "access_token": os.environ["VK_USER_TOKEN"],
                "v": "5.103",
            }

            query = requests.get(query_url, query_params)
            vk_id = query.json()["response"][0]["id"]
            new_user = Users(vk_id=vk_id)
            new_user.save()
            return redirect("student", group, new_student_id)

    context["info_form"] = info_form
    context["vk_form"] = vk_form
    context["group"] = group

    return render(request, "main/student_create.html", context)


def group(request, group):
    context = {}
    try:
        perm = Permission.objects.filter(codename=f"admin_{group}")
    except Permission.DoesNotExist:
        perm = None
    if perm in request.user.user_permissions.all():
        print("can")
    admins = User.objects.filter(
        Q(groups__permissions=perm) | Q(user_permissions=perm)
    ).distinct()
    if request.GET.get("from") == "create_group" and not admins:
        context["reg_alert"] = True
    if request.GET.get("from") == "denied_create_admin":
        context["create_admin_denied"] = True
    group_data = Groups.objects.get(group_num=group)
    students_count = len(UsersInfo.objects.filter(group_num=group))

    context["group"] = group_data
    context["students_count"] = students_count
    # context["user"] = request.user

    return render(request, "main/group.html", context)


def create_group(request):
    context = {}
    info_form = GroupInfoForm()
    sch_form = GroupScheduleForm()
    if request.method == "POST":
        info_form = GroupInfoForm(request.POST)
        sch_form = GroupScheduleForm(request.POST)
        if info_form.is_valid() and sch_form.is_valid():
            new_group = Groups(
                group_num=request.POST["group_num"],
                group_descriptor=request.POST["group_descriptor"],
            )
            new_group.save()

            new_group_sch = Schedule(
                group_num=Groups.objects.get(group_num=new_group.group_num),
                schedule_descriptor=request.POST["schedule_descriptor"],
            )
            new_group_sch.save()

            url = f"{reverse('group', kwargs={'group': new_group.group_num})}?from=create_group"

            return redirect(url)

    context["info_form"] = info_form
    context["sch_form"] = sch_form
    context["group"] = group

    return render(request, "main/group_create.html", context)


def delete_group(request, group):
    try:
        group_object = Groups.objects.get(group_num=group)
        sch = Schedule.objects.get(group_num=group)
        students = UsersInfo.objects.filter(group_num=group)
        users = [Users.objects.filter(id=st.user_id) for st in students]
    except Groups.DoesNotExist:
        raise Http404("Группа не существует.")
    else:
        group_object.delete()
        sch.delete()
        students.delete()
        for user in users:
            if user is not None:
                user.delete()
        return redirect("index")


def create_admin(request, group):
    admin_group = Group.objects.filter(name=f"admins_{group}")
    if not admin_group:
        if request.method == "POST":
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get("username")
                raw_password = form.cleaned_data.get("password1")
                ct = ContentType.objects.get_for_model(User)
                permission = Permission.objects.create(
                    codename=f"admin_{group}",
                    name=f"Can administrate group {group}",
                    content_type=ct,
                )
                permission.save()
                user = authenticate(username=username, password=raw_password)
                user.user_permissions.add(permission)
                login(request, user)
                return redirect("group", group=group)
        else:
            form = UserCreationForm()
    else:
        url = f"{reverse('group', kwargs={'group': group})}?from=denied_create_admin"
        return redirect(url)
    return render(request, "main/admin_create.html", {"form": form, "group": group})
