from django import forms

from .models import Users
from .models import StudentStatus
from .models import Groups
from .models import Schedule

from .validators import validate_vk_link


class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label="Имя")
    second_name = forms.CharField(max_length=50, label="Фамилия")
    group_num = forms.ModelChoiceField(queryset=Groups.objects.all(), label="Группа")
    subgroup_num = forms.IntegerField(label="Подгруппа")
    academic_status = forms.ModelChoiceField(
        queryset=StudentStatus.objects.all(), label="Статус студента"
    )

    class Meta:
        model = StudentStatus
        fields = [
            "first_name",
            "second_name",
            "group_num",
            "subgroup_num",
            "academic_status",
        ]


class VkForm(forms.ModelForm):
    vk_link = forms.URLField(
        label="Ссылка на страницу в ВК", validators=[validate_vk_link]
    )

    class Meta:
        model = Users
        fields = ["vk_link"]


class GroupInfoForm(forms.ModelForm):
    group_num = forms.IntegerField(label="Номер группы")
    group_descriptor = forms.CharField(max_length=30, label="Название специальности")

    class Meta:
        model = Groups
        fields = ["group_num", "group_descriptor"]


class GroupScheduleForm(forms.ModelForm):
    schedule_descriptor = forms.IntegerField(label="Дескриптор для расписания")

    class Meta:
        model = Schedule
        fields = ["schedule_descriptor"]
