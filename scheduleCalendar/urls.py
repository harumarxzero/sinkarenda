from django.urls import path
from . import views

app_name = "cal"
urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_event, name="add_event"),
    path("list/", views.get_events, name="get_events"),
    path("set_weekly_goal/", views.set_weekly_goal, name="set_weekly_goal"),
    path("weekly_goal_list/", views.weekly_goal_list, name="weekly_goal_list"),
    path("add_daily_intake/", views.add_daily_intake, name="add_daily_intake"),
    path("add_daily_intake/<str:date>/", views.add_daily_intake_with_date, name="add_daily_intake_with_date"),
    path("daily_intake_list/", views.daily_intake_list, name="daily_intake_list"),
    path("review_daily/<str:date>/", views.review_daily, name="review_daily"),
    path("daily_intakes/", views.get_daily_intakes, name="get_daily_intakes"),
    path("test/", views.test),
]