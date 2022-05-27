from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

from PIL import Image as PImage
from datetime import datetime, timedelta


class User(AbstractUser):
    account_tier = models.ForeignKey('Plan', on_delete=models.SET_NULL, null=True, default=1)


class PlanHeight(models.Model):
    height = models.PositiveIntegerField(
        validators=[MaxValueValidator(2160)],
        unique=True
    )

    def __str__(self):
        return f'{self.height}px'


class Plan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    original_link = models.BooleanField(default=False)
    generate_links = models.BooleanField(default=False)
    heights = models.ManyToManyField(PlanHeight)

    def __str__(self):
        return self.name


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.ImageField(upload_to='images/')
    thumbnails = models.ManyToManyField('Thumbnail', blank=True)
    temp_link = models.ForeignKey('TemporaryLink', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.original_file}'

    def get_original_height(self):
        return self.original_file.height


class Thumbnail(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ImageField(upload_to='thumbnails/')
    height = models.IntegerField(
        validators=[MaxValueValidator(2160)]
    )
    temp_link = models.ForeignKey('TemporaryLink', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Thumbnail, self).save(*args, **kwargs)
        image = PImage.open(self.link.path)
        percent = round(image.size[1] / self.height, 2)
        new_width = int(round(image.size[0] * percent))
        image.thumbnail((new_width, self.height))
        image.save(self.link.path)


class TemporaryLink(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    hash = models.CharField(max_length=10)
    path = models.CharField(max_length=100)
    expires_in = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(3000)]
    )
    valid_to = models.DateTimeField()

    @property
    def url(self):
        return f'http://127.0.0.1:8000/{self.hash}'

    def save(self, *args, **kwargs):
        self.valid_to = datetime.now() + timedelta(seconds=int(self.expires_in))
        super(TemporaryLink, self).save(*args, **kwargs)





