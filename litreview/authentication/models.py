from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    profile_photo = models.ImageField(verbose_name='photo de profil', default='default_profile.png',
                                      upload_to='static/img')
    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='suit'
    )

    followed_by = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='suivi par',
        related_name='followers'
    )
