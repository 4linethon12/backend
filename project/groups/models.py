from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=10)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    
class Mission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="missions")
    mission = models.CharField(max_length=16)

    def __str__(self):
        return self.mission
