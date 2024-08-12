from django.db import models
from django.db.models import Value
from django.db.models.functions import Coalesce


class DataSecurityPattern(models.Model):
    name = models.CharField(unique=True, max_length=128)
    pattern = models.CharField(unique=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DataLossMessageQuerySet(models.QuerySet):
    def annotate_has_file(self):
        return self.annotate(
            has_file=Coalesce(
                models.F("file_download_link") != "", Value(True), Value(False)
            )
        )


class DataLossMessage(models.Model):
    objects = DataLossMessageQuerySet.as_manager()

    user_id = models.CharField(max_length=128)
    text = models.TextField()
    failed_security_patterns = models.ManyToManyField(
        to=DataSecurityPattern,
        related_name="messages",
    )
    ts = models.CharField(max_length=128)
    channel = models.CharField(max_length=128)
    file_download_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["ts", "channel"]]
