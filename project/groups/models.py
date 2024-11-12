import random, string
from django.db import models
from users.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True)
    mission = models.TextField(blank=True, null=True)
    group_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="led_groups",  null=True, blank=True)

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

class RecommendedMission(models.Model):
    text = models.CharField(max_length=200)

class GroupParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')