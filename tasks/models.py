from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Priority(models.IntegerChoices):
    LOW = 1, "Low"
    MED = 2, "Medium"
    HIGH = 3, "High"

class Status(models.IntegerChoices):
    TODO = 1, "To Do"
    DOING = 2, "In Progress"
    DONE = 3, "Done"

class Task(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.MED)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-priority", "due_date", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['project', 'title'], name='unique_task_title_in_project')
        ]

    @property
    def is_overdue(self):
        return bool(self.due_date and self.status != Status.DONE and self.due_date < timezone.localdate())

    def __str__(self):
        return self.title
