from django.db import models
from django.conf import settings
from groups.models import Group

class ManitoMatch(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    giver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='giver', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', on_delete=models.CASCADE)

class ManitoMessage(models.Model):
    match = models.ForeignKey(ManitoMatch, on_delete=models.CASCADE)
    hint = models.TextField()
    letter = models.TextField()