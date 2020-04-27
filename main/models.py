import os

import requests
from django.contrib.auth.models import User
from django.db import models

from ralph_cms import settings


class StudentStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_description = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.status_description}"

    class Meta:
        db_table = "academic_statuses"


class Administrators(models.Model):
    vk_id = models.BigIntegerField(primary_key=True)
    group_num = models.ForeignKey("Groups", models.CASCADE, db_column="group_num")

    def __str__(self):
        query_url = "https://api.vk.com/method/users.get"
        query_params = {
            "user_ids": self.vk_id,
            "access_token": os.environ["VK_USER_TOKEN"],
            "v": "5.103",
        }

        query = requests.get(query_url, query_params)
        first_name = query.json()["response"][0]["first_name"]
        last_name = query.json()["response"][0]["last_name"]

        return f"{first_name} {last_name} {self.group_num}"

    class Meta:
        db_table = "administrators"


class Calls(models.Model):
    session_id = models.IntegerField(blank=True, null=False, primary_key=True)
    ids = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        db_table = "calls"


class FinancesCategories(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    sum = models.IntegerField(blank=True, null=True)
    group_num = models.ForeignKey("Groups", models.CASCADE, db_column="group_num")

    class Meta:
        db_table = "finances_categories"


class FinancesDonates(models.Model):
    student_id = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(
        FinancesCategories, models.CASCADE, db_column="category", blank=True, null=True,
    )
    sum = models.IntegerField(blank=True, null=True)
    created_date = models.DateField(blank=True, null=True)
    updated_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "finances_donates"


class FinancesExpenses(models.Model):
    category = models.ForeignKey(
        FinancesCategories, models.CASCADE, db_column="category", blank=True, null=True,
    )
    sum = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "finances_expenses"


class Groups(models.Model):
    group_num = models.IntegerField(primary_key=True)
    group_descriptor = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.group_descriptor} ({self.group_num})"

    class Meta:
        db_table = "groups"


class MailingMgmt(models.Model):
    session_id = models.IntegerField(blank=True, null=False, primary_key=True)
    mailing = models.IntegerField(blank=True, null=True)
    m_text = models.CharField(max_length=1000, blank=True, null=True)
    m_attach = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "mailing_mgmt"


class Mailings(models.Model):
    mailing_id = models.AutoField(primary_key=True)
    mailing_name = models.CharField(unique=True, max_length=30)
    group_num = models.ForeignKey(Groups, models.CASCADE, db_column="group_num")
    default_status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "mailings"


class Schedule(models.Model):
    group_num = models.OneToOneField(
        Groups, models.CASCADE, db_column="group_num", primary_key=True
    )
    schedule_descriptor = models.IntegerField(unique=True, blank=True, null=True)

    class Meta:
        db_table = "schedule"


class Sessions(models.Model):
    vk_id = models.IntegerField(unique=True, blank=True, null=True)
    state = models.CharField(max_length=35, blank=True, null=True)
    conversation = models.IntegerField(blank=True, null=True)
    names_using = models.SmallIntegerField(blank=True, null=True)
    fin_cat = models.CharField(max_length=120, blank=True, null=True)
    donate_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "sessions"


class Subscriptions(models.Model):
    user_id = models.IntegerField(primary_key=True)
    mailing_id = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        db_table = "subscriptions"


class Texts(models.Model):
    session_id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=1200, blank=True, null=True)
    attach = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "texts"


class Users(models.Model):
    vk_id = models.BigIntegerField(unique=True)

    class Meta:
        db_table = "users"


class UsersInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    group_num = models.SmallIntegerField()
    subgroup_num = models.SmallIntegerField()
    academic_status = models.ForeignKey(
        StudentStatus, models.CASCADE, db_column="status_id"
    )

    def __str__(self):
        return (
            f"{self.second_name} {self.first_name} (группа {self.group_num}/"
            f"{self.subgroup_num}). Статус: {self.academic_status}"
        )

    class Meta:
        db_table = "users_info"
