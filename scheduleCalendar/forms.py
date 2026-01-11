from django import forms
from .models import WeeklyGoal, DailyIntake


class EventForm(forms.Form):

    start_date = forms.IntegerField(required=True)
    end_date = forms.IntegerField(required=True)
    event_name = forms.CharField(required=True, max_length=32)

class CalendarForm(forms.Form):

    start_date = forms.IntegerField(required=True)
    end_date = forms.IntegerField(required=True)


class WeeklyGoalForm(forms.ModelForm):
    class Meta:
        model = WeeklyGoal
        fields = ['week_start', 'meet_goal', 'fish_goal', 'rice_goal', 'vege_goal', 'men_goal', 'pan_goal']
        labels = {
            'week_start': '週開始日',
            'meet_goal': '肉の目標量',
            'fish_goal': '魚の目標量',
            'rice_goal': '米の目標量',
            'vege_goal': '野菜の目標量',
            'men_goal': '麺の目標量',
            'pan_goal': 'パンの目標量',
        }
        widgets = {
            'week_start': forms.DateInput(attrs={'type': 'date'}),
        }


class DailyIntakeForm(forms.ModelForm):
    class Meta:
        model = DailyIntake
        fields = ['date', 'meet_intake', 'fish_intake', 'rice_intake', 'vege_intake', 'men_intake', 'pan_intake']
        labels = {
            'date': '摂取日',
            'meet_intake': '肉の摂取量',
            'fish_intake': '魚の摂取量',
            'rice_intake': '米の摂取量',
            'vege_intake': '野菜の摂取量',
            'men_intake': '麺の摂取量',
            'pan_intake': 'パンの摂取量',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }