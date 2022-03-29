from __future__ import annotations
from pyexpat import model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Margin(models.Model):
    margin_num = models.CharField(max_length=50, primary_key=True)
    Bbox = models.ForeignKey("Bbox", on_delete=models.CASCADE, db_column="bbox")
    real_margin = models.IntegerField()
    margin_ratio = models.IntegerField()
class Box_segmentation(models.Model):
    segmentation_name = models.CharField(max_length=50, primary_key=True)
    Bbox = models.ForeignKey("Bbox", on_delete=models.CASCADE, db_column="bbox")
    segmentation_point = models.IntegerField()

class Bbox(models.Model):
    box_name = models.CharField(max_length=50, primary_key=True)
    anotations = models.ForeignKey("Anotations", on_delete=models.CASCADE, db_column="anotations")
    min_margn_ratio = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)])
    box_min_x = models.IntegerField()
    box_min_y = models.IntegerField()
    box_width = models.IntegerField()
    box_height = models.IntegerField()
    #box_segmentation = models.ManyToManyField(Box_segmentation)
    #margin = models.ManyToManyField(Box_segmentation)

    # def __str__(self):
    #     return self.data + self.cut_off


class Anotations(models.Model):
    anotation_name = models.CharField(max_length=50, primary_key=True)
    data = models.ForeignKey("Data", on_delete=models.CASCADE, db_column="data")
    cut_off = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    # class Meta:
    #     unique_together = (('data', 'cut_off'))
    #bbox = models.ManyToManyField(Bbox, related_name='data.Anotations.bbox')

    def __str__(self):
        return str(self.data) + '_' + str(self.cut_off)

class Data(models.Model):
    img_name = models.CharField(max_length=50, primary_key=True)
    image = models.ImageField(upload_to='')
    # annotations = models.ManyToManyField(Anotations, related_name='anotations')

    def __str__(self):
        return self.name




