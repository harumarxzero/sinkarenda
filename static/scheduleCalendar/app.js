document.addEventListener('DOMContentLoaded', function() {
    console.log('app.js loaded');
    var calendarEl = document.getElementById('calendar');
    console.log('calendarEl:', calendarEl);

    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'en',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            // イベントを取得
            axios.post('/get_events/', {
                start_date: fetchInfo.start.getTime(),
                end_date: fetchInfo.end.getTime()
            })
            .then(function(response) {
                var events = response.data;
                // 日次摂取も取得
                axios.post('/get_daily_intakes/', {
                    start_date: fetchInfo.start.getTime(),
                    end_date: fetchInfo.end.getTime()
                })
                .then(function(response2) {
                    var intakes = response2.data;
                    successCallback(events.concat(intakes));
                })
                .catch(function(error) {
                    console.error(error);
                    successCallback(events);
                });
            })
            .catch(function(error) {
                console.error(error);
                failureCallback(error);
            });
        },
        eventClick: function(info) {
            // イベントクリック時の処理
            if (info.event.title.includes('週合計')) {
                // 週合計の場合、何もしない
                return;
            }
            var date = info.event.start.toISOString().split('T')[0];
            window.location.href = '/add_daily_intake/' + date + '/';
        }
    });

    calendar.render();
    console.log('Calendar rendered with locale:', calendar.getOption('locale'));
});</content>
<parameter name="filePath">c:\Users\nakan\OneDrive\デスクトップ\tkcalendar\static\scheduleCalendar\app.js