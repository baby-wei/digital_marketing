from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse
from django.utils.text import slugify 

from sellers.models import SellerAccount

def download_media_location(instance, filename):
	return "%s/%s" %(instance.slug, filename)

class Product(models.Model):
	"""
	# Each product - 1 user, Each user - 1 product
	# user = models.OneToOneField(settings.AUTH_USER_MODEL)
	# Each product - 1 user, Each user - multiple products
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	# Each product - multiple users, Each user - multiple products
	managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="managers_products", blank=True)
	"""
	seller = models.ForeignKey(SellerAccount)
	media = models.ImageField(blank=True, 
				null=True, 
				upload_to=download_media_location,
				storage=FileSystemStorage(location=settings.PROTECTED_ROOT))
	title = models.CharField(max_length=30)
	slug = models.SlugField(blank=True, unique=True)
	description = models.TextField()
	price = models.DecimalField(max_digits=100, decimal_places=2, default=9.99) 
	sale_active = models.BooleanField(default=False)
	sale_price = models.DecimalField(max_digits=100, 
		decimal_places=2, default=9.99, null=True, blank=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		# using url names makes it more dynamic; kwarg = (?P<slug>[\w-]+)
		view_name = "products:detail_slug"
		return reverse(view_name, kwargs={"slug": self.slug})

	def get_edit_url(self):
		# using url names makes it more dynamic; kwarg = (?P<slug>[\w-]+)
		view_name = "sellers:product_edit"
		return reverse(view_name, kwargs={"pk": self.id})

	def get_download(self):
		# get the /download to redirect to ProductDownloadView
		view_name = "products:download_slug"
		url = reverse(view_name, kwargs={"slug": self.slug})
		return url 

	# property turns the f(x) into an attribute of this instance
	# calling can just be get_price instead of get_price()
	@property
	def get_price(self):
		if self.sale_price and self.sale_active:
			return self.sale_price
		return self.price

	def get_html_price(self):
		price = self.get_price			
		if price == self.sale_price:
			return "<p><span>%s</span> <span style='color:red; text-decoration:line-through;'>%s</span> </p>" %(self.sale_price, self.price)
		else:
 			return "<p>%s</p>" %(self.price)


def create_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug

	qs = Product.objects.filter(slug=slug)
	exists = qs.exists()
	if exists:
		# qs.first().id is used instead of instance.id
		# this is related to how pre-save fx works: 
		# bcoz it hasn't been saved yet, an id is not created
		new_slug = "%s-%s" %(slug, qs.first().id)
		# You don wanna jus return a new slug, you wanna go thro fx again
		# and check that this new slug actually doesn't exist
		return create_slug(instance, new_slug=new_slug)
	return slug 

def product_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)




# def product_post_save_reciever(sender, instance, *args, **kwargs):
# 	if instance.slug != slugify(instance.title):
# 		instance.slug = slugify(instance.title)
# 		instance.save()

# post_save.connect(product_pre_save_reciever, sender=Product)


def thumbnail_location(instance, filename):
	return "%s/%s" %(instance.product.slug, filename)

THUMB_CHOICES = (
		("hd", "HD"),
		("sd", "SD"),
		("micro", "Micro"),
)

class Thumbnail(models.Model):
	product = models.ForeignKey(Product)
	type = models.CharField(max_length=20, choices=THUMB_CHOICES, default='hd')
	height = models.CharField(max_length=20, null=True, blank=True)
	width = models.CharField(max_length=20, null=True, blank=True)
	media = models.ImageField(
		width_field= "width",
		height_field= "height",
		blank=True, 
		null=True, 
		upload_to=thumbnail_location,
	)

	def __str__(self):
		return str(self.media.path)


import os
import shutil
from PIL import Image
import random

from django.core.files import File 

def create_new_thumb(media_path, instance, owner_slug, max_length, max_width):
	# 'basename' will gv us the actual filename at the end of this path
	filename = os.path.basename(media_path)
	thumb = Image.open(media_path)
	size = (max_length, max_width)
	thumb.thumbnail(size, Image.ANTIALIAS)

	temp_loc = "%s/%s/tmp" %(settings.MEDIA_ROOT, owner_slug)
	if not os.path.exists(temp_loc):
		os.makedirs(temp_loc)
		
	temp_file_path = os.path.join(temp_loc, filename)
	if os.path.exists(temp_file_path):
		temp_path = os.path.join(temp_loc, "%s" %(random.random()))
		os.makedirs(temp_path)
		temp_file_path = os.path.join(temp_path, filename)

	temp_image = open(temp_file_path, "wb")
	thumb.save(temp_image)
	thumb_data = open(temp_file_path, "rb")

	thumb_file = File(thumb_data)
	instance.media.save(filename, thumb_file)

	shutil.rmtree(temp_loc, ignore_errors=True)
	return True


def product_post_save_receiver(sender, instance, created, *args, **kwargs):
	if instance.media:
		hd, hd_created = Thumbnail.objects.get_or_create(product=instance, type='hd')
		sd, sd_created = Thumbnail.objects.get_or_create(product=instance, type='sd')
		micro, micro_created = Thumbnail.objects.get_or_create(product=instance, type='micro')

		hd_max = (500, 500)
		sd_max = (350, 350)
		micro_max = (150, 150)

		media_path = instance.media.path 
		owner_slug = instance.slug 

		if hd_created:
			create_new_thumb(media_path, hd, owner_slug, hd_max[0], hd_max[1])

		if sd_created:
			create_new_thumb(media_path, sd, owner_slug, sd_max[0], sd_max[1])

		if micro_created:
			create_new_thumb(media_path, micro, owner_slug, micro_max[0], micro_max[1])
	

post_save.connect(product_post_save_receiver, sender=Product)


class MyProducts(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	products = models.ManyToManyField(Product, blank=True)

	def __str__(self):
		return "%s" %(self.products.count())

	class Meta:
		verbose_name = "My Products"
		verbose_name_plural = "My Products"

class ProductRating(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	product = models.ForeignKey(Product)
	rating = models.IntegerField(null=True, blank=True)
	verified = models.BooleanField(default=False)

	def __str__(self):
		return "%s" %(self.rating)


class CuratedProducts(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	section_name = models.CharField(max_length=120)
	products = models.ManyToManyField(Product, blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.section_name