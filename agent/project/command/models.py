import os.path

from django.db import models
from agent.project.models import Project
from pathlib import Path

class Command(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='commands')
    command = models.CharField(max_length=300)
    cwd = models.CharField(max_length=300, null=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    restart_command = models.BooleanField(default=False, help_text='If enabled, runs the command when the project restarts')
    registered_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.command}"

    class Meta:
        db_table = "command"
        verbose_name = "Command"
        verbose_name_plural = "Commands"

    @property
    def _cwd(self):
        """
        Returns the current working directory for the command execution.
        If 'cwd' is set, it returns that value; otherwise, it returns the project's path.
        """

        if not self.cwd:
            return Path(self.project.path)

        # If 'cwd' is a relative path, combine it with the project's path
        return Path(self.cwd) if os.path.isabs(self.cwd) else Path(self.project.path) / self.cwd

    def execute(self):
        import subprocess

        try:
            result = subprocess.run(self.command,
                                    cwd=self._cwd,
                                    shell=True,
                                    check=True,
                                    capture_output=True,
                                    text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred while executing the command: {e.stderr}"
