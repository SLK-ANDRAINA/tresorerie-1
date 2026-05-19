from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# ===================================================================
# MANAGER FOR CUSTOM USER
# ===================================================================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        extra_fields.pop('username', None)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# ===================================================================
# CUSTOM USER MODEL
# ===================================================================
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ===================================================================
# CAISSE MODEL
# ===================================================================
class Caisse(models.Model):
    TYPE_CAISSE_CHOICES = [
        ('Grande Caisse', 'Grande Caisse'),
        ('Petite Caisse', 'Petite Caisse'),
    ]

    TYPE_OPERATION_CHOICES = [
        ('Entrée', 'Entrée'),
        ('Sortie', 'Sortie'),
    ]

    type_caisse = models.CharField(max_length=20, choices=TYPE_CAISSE_CHOICES)
    type_operation = models.CharField(max_length=10, choices=TYPE_OPERATION_CHOICES)
    date = models.DateField()
    motif = models.TextField()
    somme = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type_caisse} - {self.type_operation} - {self.somme}ar"