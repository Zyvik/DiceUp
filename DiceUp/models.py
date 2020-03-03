from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class DiceUpModel(models.Model):
    original_picture = models.ImageField(upload_to='DiceUp/')
    dice_picture = models.ImageField(default=None)
    instruction = models.FileField(default=None)


# deletes original and DiceUp picture when deleting models.
@receiver(post_delete, sender=DiceUpModel)
def submission_delete(sender, instance, **kwargs):
    instance.original_picture.delete(False)
    instance.dice_picture.delete(False)
    instance.instruction.delete(False)
