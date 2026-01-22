from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


# -----------------------
# Category Model
# -----------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        """Creates a url to data, then we generate the name"""

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ------------------------
# Tag Model
# -------------------------

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        """
        The same check like Category Model
        Creates a url to data
        """

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# --------------------------
# Post Model
# --------------------------

class Post(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS_OF_THE_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published')
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    content = models.TextField()

    # Connection with User table (from Models)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/%Y/%m/%d', blank=True, null=True)

    # Connection with Category table (from Models)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_OF_THE_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        # Sorting by default to descending date

        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def save(self, *args, **kwargs):
        """
        Generated the title with if not check,
        and with while check - we guarantee unique
        """

        if not self.slug:
            base = slugify(self.title)
            slug = base
            index = 1

            while Post.objects.filter(slug=slug).exists():
                slug = f"{base}-{index}"
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returning to a detail page"""
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def total_likes(self):
        """Calculate likes"""
        return self.likes.count()


# --------------------------
# Comment Model
# --------------------------

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()

    # Reply of the comment

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self): return f'Comment by {self.user} on {self.post}'


# --------------------------
# Profile Model + Signals
# --------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)

    # Information about user
    bio = models.TextField(blank=True)

    def __str__(self): return f'Profile of {self.user.username}'


# -------------------
# Signals
# -------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """"Signals for automatic create or saves the profile(checks only)"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
