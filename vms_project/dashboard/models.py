from django.db import models


class Department(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="departments"
    )
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.organization.code})"


class JobRole(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="job_roles"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_roles"
    )
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class MailTemplate(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="mail_templates"
    )

    # used internally in code (ex: VISITOR_APPROVED)
    key = models.CharField(max_length=100)

    # optional UI display title
    title = models.CharField(max_length=200, blank=True)

    subject = models.CharField(max_length=255)
    body = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "key")
        ordering = ["key"]

    def __str__(self):
        return self.key


class Employee(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="employees"
    )

    employee_id = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )

    job_role = models.ForeignKey(
        JobRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees"
    )

    class Meta:
        unique_together = ("organization", "employee_id")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.employee_id})"