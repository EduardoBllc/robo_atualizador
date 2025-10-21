from django.db import models
import git
from datetime import datetime

class Project(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=128)
    registered_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    commands = models.ManyToManyField('Command', blank=True, related_name='aplicacoes')
    remote = models.CharField(max_length=64, default='origin')
    branch_trunc = models.CharField(max_length=64, default='main')
    branch_dev = models.CharField(max_length=64, blank=True, null=True)
    branch_homolog = models.CharField(max_length=64, blank=True, null=True)
    branch_prod = models.CharField(max_length=64, blank=True, null=True)
    auto_update = models.BooleanField(default=True, help_text="If enabled, the project will be automatically updated.")

    def __str__(self):
        return f"{self.name}({self.path})"

    class Meta:
        db_table = "project"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["name"]

    @property
    def git_repository(self):
        return git.Repo(self.path)

    @property
    def active_branch(self) -> git.Head | None:
        try:
            return self.git_repository.active_branch
        except TypeError:
            return None

    @property
    def actual_commit(self) -> git.Commit:
        return self.git_repository.head.commit

    @property
    def actual_commit_date(self) -> datetime:
        return self.actual_commit.committed_datetime

    @property
    def formatted_actual_commit(self) -> str:
        return f"{self.actual_commit.hexsha[:7]} - {self.actual_commit_date.strftime('%d/%m/%Y')}"

class Command(models.Model):
    command = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    registered_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.command}"

    class Meta:
        db_table = "command"
        verbose_name = "Command"
        verbose_name_plural = "Commands"

