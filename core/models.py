from django.db import models

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=50)
    message = models.TextField()
    source = models.CharField(max_length=100)

    def __str__(self):
        message = self.message

        if len(message) > 50:
            message = message[:47] + "..."
        return f"[{self.timestamp}] {self.level} - {self.source}: {message}"
