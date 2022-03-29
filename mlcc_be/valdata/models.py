from __future__ import annotations
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Margin(models.Model):
    margin_num = models.CharField(max_length=50, primary_key=True)
    bbox_name = models.ForeignKey("Bbox", on_delete=models.CASCADE, db_column="bbox")
    margin_x = models.IntegerField()
    real_margin = models.FloatField()
    margin_ratio = models.FloatField()
    margin_width = models.FloatField()
    cut_off = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    

class Bbox(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    data_name = models.ForeignKey("Data", on_delete=models.CASCADE, db_column="data")
    min_margn_ratio = models.FloatField()
    box_min_x = models.IntegerField()
    box_min_y = models.IntegerField()
    box_width = models.IntegerField()
    box_height = models.IntegerField()

    def __str__(self):
        return self.box_name


class Data(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    original_image = models.ImageField(upload_to='')
    original_image = models.ImageField(upload_to='')

    def __str__(self):
        return self.name




