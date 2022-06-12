from django.db import models


class Permission(models.Model):
	app = models.CharField(max_length=20, null=True, blank=False)
	desc = models.CharField(max_length=30, null=True, blank=False)
	code = models.CharField(max_length=20, null=True, blank=False)
	value = models.BooleanField(default=False, blank=True)

	class Meta:
		unique_together = ('app', 'code')


class Role(models.Model):
	name = models.CharField(max_length=20, null=True, blank=False, unique=True)
	created = models.DateTimeField(null=True, blank=True)
	modified = models.DateTimeField(null=True, blank=True)


	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		from django.utils import timezone

		new = self._state.adding

		if new:
			self.created = timezone.now()
		else:
			self.modified = timezone.now()

		super(Role, self).save()

	class Meta:
		ordering = '-created',
		

class RolePerm(models.Model):
	app = models.CharField(max_length=20, null=True, blank=False)
	desc = models.CharField(max_length=30, null=True, blank=False)
	code = models.CharField(max_length=20, null=True, blank=False)
	value = models.BooleanField(blank=True, default=False)
	role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)