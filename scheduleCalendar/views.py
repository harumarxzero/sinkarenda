import json
from .models import Event, WeeklyGoal, DailyIntake
from .forms import CalendarForm, EventForm, WeeklyGoalForm, DailyIntakeForm
from django.http import Http404
from django.http import JsonResponse
import time
from django.template import loader
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from datetime import datetime, timedelta

# Create your views here.


def index(request):
    """
    カレンダー画面
    """
    # CSRFのトークンを発行する
    get_token(request)

    # 今週のフィードバックを計算
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    feedback_messages = []
    try:
        goal = WeeklyGoal.objects.get(week_start=monday)
        week_intakes = DailyIntake.objects.filter(date__gte=monday, date__lte=sunday)
        current = {
            'meet': sum(i.meet_intake for i in week_intakes),
            'fish': sum(i.fish_intake for i in week_intakes),
            'rice': sum(i.rice_intake for i in week_intakes),
            'vege': sum(i.vege_intake for i in week_intakes),
            'men': sum(i.men_intake for i in week_intakes),
            'pan': sum(i.pan_intake for i in week_intakes),
        }
        foods = [
            ('肉', 'meet', goal.meet_goal),
            ('魚', 'fish', goal.fish_goal),
            ('米', 'rice', goal.rice_goal),
            ('野菜', 'vege', goal.vege_goal),
            ('麺', 'men', goal.men_goal),
            ('パン', 'pan', goal.pan_goal),
        ]
        
        # 各食品のフィードバック
        for name, key, target in foods:
            intake = current[key]
            if target == 0:
                feedback_messages.append(f"{name}の目標が設定されていないよ。目標を設定しよう！")
            elif intake < target:
                feedback_messages.append(f"{name}は目標{target}回に対して{intake}回しか摂取できてないよ。もう少し頑張ろう！")
            elif intake == target:
                feedback_messages.append(f"{name}は目標{target}回ちょうど摂取できたね。素晴らしい！")
            else:
                feedback_messages.append(f"{name}は目標{target}回を超えて{intake}回摂取できたよ。すごい！")
        
        # 特に多いもの、少ないものを分析
        differences = [(name, intake - target) for name, _, target in [(name, key, getattr(goal, f'{key}_goal')) for name, key, _ in foods] for intake in [current[key]]]
        differences = [(name, diff) for (name, _, _), (_, diff) in zip(foods, differences)]
        
        # 不足が多いもの (diff < 0, 絶対値が大きい)
        shortages = sorted([(name, abs(diff)) for name, diff in differences if diff < 0], key=lambda x: x[1], reverse=True)
        if shortages:
            top_shortage = shortages[0][0]
            feedback_messages.append(f"特に{top_shortage}の摂取が足りてないね。意識して摂取しよう！")
        
        # 超過が多いもの (diff > 0, 値が大きい)
        excesses = sorted([(name, diff) for name, diff in differences if diff > 0], key=lambda x: x[1], reverse=True)
        if excesses:
            top_excess = excesses[0][0]
            feedback_messages.append(f"{top_excess}は目標を大きく超えて摂取できてるよ。バランスが取れてる！")
        
    except WeeklyGoal.DoesNotExist:
        feedback_messages.append("今週の目標が設定されていないよ。まずは目標を設定しよう！")

    template = loader.get_template("scheduleCalendar/index.html")
    context = {'feedback_messages': feedback_messages}
    return HttpResponse(template.render(context, request))


def add_event(request):
    """
    イベント登録
    """

    if request.method == "GET":
        # GETは対応しない
        raise Http404()

    # JSONの解析
    datas = json.loads(request.body)

    # バリデーション
    eventForm = EventForm(datas)
    if eventForm.is_valid() == False:
        # バリデーションエラー
        raise Http404()

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]
    event_name = datas["event_name"]

    # 日付に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_date = time.strftime(
        "%Y-%m-%d", time.localtime(start_date / 1000))
    formatted_end_date = time.strftime(
        "%Y-%m-%d", time.localtime(end_date / 1000))

    # 登録処理
    event = Event(
        event_name=str(event_name),
        start_date=formatted_start_date,
        end_date=formatted_end_date,
    )
    event.save()

    # 空を返却
    return HttpResponse("")


def get_events(request):
    """
    イベントの取得
    """

    if request.method == "GET":
        # GETは対応しない
        raise Http404()

    # JSONの解析
    datas = json.loads(request.body)

    # バリデーション
    calendarForm = CalendarForm(datas)
    if calendarForm.is_valid() == False:
        # バリデーションエラー
        raise Http404()

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]

    # 日付に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_date = time.strftime(
        "%Y-%m-%d", time.localtime(start_date / 1000))
    formatted_end_date = time.strftime(
        "%Y-%m-%d", time.localtime(end_date / 1000))

    # FullCalendarの表示範囲のみ表示
    events = Event.objects.filter(
        start_date__lt=formatted_end_date, end_date__gt=formatted_start_date
    )

    # fullcalendarのため配列で返却
    list = []
    for event in events:
        list.append(
            {
                "title": event.event_name,
                "start": event.start_date,
                "end": event.end_date,
            }
        )

    return JsonResponse(list, safe=False)


def get_daily_intakes(request):
    """
    日次摂取と週合計の取得
    """

    if request.method == "GET":
        raise Http404()

    datas = json.loads(request.body)

    start_date = datas["start_date"]
    end_date = datas["end_date"]

    formatted_start_date = time.strftime(
        "%Y-%m-%d", time.localtime(start_date / 1000))
    formatted_end_date = time.strftime(
        "%Y-%m-%d", time.localtime(end_date / 1000))

    # DailyIntake
    intakes = DailyIntake.objects.filter(
        date__lt=formatted_end_date, date__gt=formatted_start_date
    )

    list = []
    for intake in intakes:
        title = f"肉:{intake.meet_intake}\n魚:{intake.fish_intake}\n米:{intake.rice_intake}\n野菜:{intake.vege_intake}\n麺:{intake.men_intake}\nパン:{intake.pan_intake}"
        list.append(
            {
                "title": title,
                "start": intake.date,
                "end": intake.date,
                "allDay": True,
            }
        )

    # 週合計 (土曜日)
    from datetime import datetime, timedelta
    current = datetime.strptime(formatted_start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(formatted_end_date, "%Y-%m-%d")
    while current <= end_dt:
        if current.weekday() == 5:  # 土曜日
            week_start = current - timedelta(days=6)  # 月曜日
            week_intakes = DailyIntake.objects.filter(date__gte=week_start.date(), date__lte=current.date())
            total = {
                'meet': sum(i.meet_intake for i in week_intakes),
                'fish': sum(i.fish_intake for i in week_intakes),
                'rice': sum(i.rice_intake for i in week_intakes),
                'vege': sum(i.vege_intake for i in week_intakes),
                'men': sum(i.men_intake for i in week_intakes),
                'pan': sum(i.pan_intake for i in week_intakes),
            }
            try:
                goal = WeeklyGoal.objects.get(week_start=week_start.date())
                goals = {
                    'meet': goal.meet_goal,
                    'fish': goal.fish_goal,
                    'rice': goal.rice_goal,
                    'vege': goal.vege_goal,
                    'men': goal.men_goal,
                    'pan': goal.pan_goal,
                }
            except WeeklyGoal.DoesNotExist:
                goals = {k: 0 for k in total.keys()}
            title = f"週合計\n肉:摂取{total['meet']}/目標{goals['meet']}\n魚:摂取{total['fish']}/目標{goals['fish']}\n米:摂取{total['rice']}/目標{goals['rice']}\n野菜:摂取{total['vege']}/目標{goals['vege']}\n麺:摂取{total['men']}/目標{goals['men']}\nパン:摂取{total['pan']}/目標{goals['pan']}"
            list.append(
                {
                    "title": title,
                    "start": current.date(),
                    "end": current.date(),
                    "allDay": True,
                    "className": "weekly-total",
                }
            )
        current += timedelta(days=1)

    return JsonResponse(list, safe=False)

def set_weekly_goal(request):
    # 現在の週の月曜日をデフォルト値にする
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())  # 月曜日
    if request.method == 'POST':
        form = WeeklyGoalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cal:weekly_goal_list')
    else:
        form = WeeklyGoalForm(initial={'week_start': monday})
    return render(request, 'scheduleCalendar/set_weekly_goal.html', {'form': form})


def weekly_goal_list(request):
    goals = WeeklyGoal.objects.all().order_by('-week_start')
    return render(request, 'scheduleCalendar/weekly_goal_list.html', {'goals': goals})


def add_daily_intake(request):
    if request.method == 'POST':
        form = DailyIntakeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('daily_intake_list')
    else:
        form = DailyIntakeForm(initial={'date': datetime.now().date()})
    return render(request, 'scheduleCalendar/add_daily_intake.html', {'form': form})

def add_daily_intake_with_date(request, date):
    if request.method == 'POST':
        form = DailyIntakeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cal:daily_intake_list')
    else:
        form = DailyIntakeForm(initial={'date': date})
    return render(request, 'scheduleCalendar/add_daily_intake.html', {'form': form})

def daily_intake_list(request):
    intakes = DailyIntake.objects.all().order_by('-date')
    return render(request, 'scheduleCalendar/daily_intake_list.html', {'intakes': intakes})


def review_daily(request, date):
    try:
        intake = DailyIntake.objects.get(date=date)
    except DailyIntake.DoesNotExist:
        intake = None

    # 週の開始日を計算 (月曜日)
    week_start = date - timedelta(days=date.weekday())
    try:
        goal = WeeklyGoal.objects.get(week_start=week_start)
        goals = [goal.meet_goal, goal.fish_goal, goal.rice_goal, goal.vege_goal, goal.men_goal, goal.pan_goal]
    except WeeklyGoal.DoesNotExist:
        goals = [0] * 6

    if intake:
        intakes = [intake.meet_intake, intake.fish_intake, intake.rice_intake, intake.vege_intake, intake.men_intake, intake.pan_intake]
    else:
        intakes = [0] * 6

    food_names = ['肉', '魚', '米', '野菜', '麺', 'パン']
    comparisons = []
    for i in range(6):
        diff = intakes[i] - goals[i]
        if diff > 0:
            status = f"目標よりも{diff}回多く摂取しました。"
        elif diff == 0:
            status = "目標通りです。"
        else:
            status = f"目標よりも{abs(diff)}回少なく摂取しました。"
        comparisons.append({
            'name': food_names[i],
            'goal': goals[i],
            'intake': intakes[i],
            'status': status
        })

    return render(request, 'scheduleCalendar/review_daily.html', {
        'date': date,
        'comparisons': comparisons
    })





from django.http import HttpResponse

def test(request):
    return HttpResponse("Render OK")







