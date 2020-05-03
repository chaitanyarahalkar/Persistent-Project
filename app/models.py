from django.db import models

# Create your models here.
class Case(models.Model):

	QUALITY = (('O', 'Outstanding'), ('G','Good'), ('S','Satisfactory'))

	case_id = models.AutoField(auto_created = True, primary_key = True, verbose_name = 'Case ID')
	next_visit = models.IntegerField(default = 0, verbose_name = 'Days Before Next Visit')
	kvp = models.FloatField(default = 0.0, verbose_name = 'kVp')
	ma = models.FloatField(default = 0.0, verbose_name = 'mA')
	dlp = models.FloatField(default = 0.0, verbose_name = 'DLP')
	diagnostic_quality = models.CharField(max_length = 1, choices = QUALITY)
	see_physician = models.BooleanField(default = False)
	comments = models.TextField()
	patient_id = models.CharField(max_length = 150)

	class Meta:
		verbose_name = 'Case'
		verbose_name_plural = 'Cases'

	def __str__(self):
		return self.patient_id


class Nodule(models.Model):
	POSITION = (('L','Left'), ('R', 'Right'))
	STATE = (('SL','Solid'),('SS','Semi Solid'),('GG','Ground Glass'))
	SIZE = (('UC','Unchanged'),('IN','Increased'),('DC','Decreased'),('NW','New'))

	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	position = models.CharField(max_length = 1, choices = POSITION)
	state = models.CharField(max_length = 2, choices = STATE)
	size = models.CharField(max_length = 2, choices = SIZE)
	notes = models.TextField()
	fig = models.ImageField(upload_to = 'Uploads/', verbose_name = 'Nodule Image')
	x = models.FloatField(default = 0.0)
	y = models.FloatField(default = 0.0)
	z = models.FloatField(default = 0.0)
	score = models.FloatField(default = 0.0)
	slice_index = models.IntegerField(default = 0, verbose_name = 'Slice Index')
	diameter = models.FloatField(default = 0.0)
	probability = models.FloatField(default = 0.0)


	class Meta:
		verbose_name = 'Nodule'
		verbose_name_plural = 'Nodules'

	def __str__(self):
		return str(self.id)
