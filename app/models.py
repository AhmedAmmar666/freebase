from django.db import models
from django.utils.text import slugify


class Category(models.Model):
	name = models.CharField(max_length=200, unique=True)
	slug = models.SlugField(max_length=200, unique=True)

	class Meta:
		verbose_name_plural = 'categories'

	def __str__(self):
		return self.name


class Tool(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tools')
	name = models.CharField(max_length=200)
	tagline = models.CharField(max_length=300, blank=True)
	description = models.TextField(blank=True)
	url = models.URLField(max_length=500)
	host = models.CharField(max_length=200, blank=True)
	logo = models.ImageField(upload_to='logos/', blank=True, null=True)
	featured = models.BooleanField(default=False)
	accent = models.CharField(max_length=50, blank=True)
	glyph = models.CharField(max_length=10, blank=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not hasattr(self, 'slug'):
			# derive a slug-like attribute if needed (not stored field)
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)
