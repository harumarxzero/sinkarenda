from django.db import models

# Create your models here.


class Event(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    event_name = models.CharField(max_length=200)


class WeeklyGoal(models.Model):
    week_start = models.DateField(unique=True)  # 週の開始日 (月曜日)
    meet_goal = models.IntegerField(default=0)  # 肉
    fish_goal = models.IntegerField(default=0)  # 魚
    rice_goal = models.IntegerField(default=0)  # 米
    vege_goal = models.IntegerField(default=0)  # 野菜
    men_goal = models.IntegerField(default=0)   # 麺
    pan_goal = models.IntegerField(default=0)   # パン


class DailyIntake(models.Model):
    date = models.DateField(unique=True)
    meet_intake = models.IntegerField(default=0)
    fish_intake = models.IntegerField(default=0)
    rice_intake = models.IntegerField(default=0)
    vege_intake = models.IntegerField(default=0)
    men_intake = models.IntegerField(default=0)
    pan_intake = models.IntegerField(default=0)