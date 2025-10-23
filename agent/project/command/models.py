from django.db import models

class Command(models.Model):
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, related_name='project')
    command = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    restart_command = models.BooleanField(default=False, help_text='If is enabled, run the command when calls the project\'s restart')
    registered_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.command}"

    class Meta:
        db_table = "command"
        verbose_name = "Command"
        verbose_name_plural = "Commands"