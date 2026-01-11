// CSRF対策
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
axios.defaults.xsrfCookieName = "csrftoken"

document.addEventListener('DOMContentLoaded', function () {
    console.log('app.js loaded');
    var calendarEl = document.getElementById('calendar');
    console.log('calendarEl:', calendarEl);

    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'ja',
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        // 日付をクリック
        dateClick: function(info) {
            window.location.href = '/sc/add_daily_intake/' + info.dateStr + '/';
        },

        eventContent: function(arg) {
            let html = arg.event.title.replace(/\n/g, '<br>');
            // 週合計以外も黒い文字にする
            html = '<span style="color: black; font-weight: bold;">' + html + '</span>';
            return { html: html };
        },

        eventClick: function(info) {
            // イベントクリック時の処理
            if (info.event.title.includes('週合計')) {
                // 週合計の場合、何もしない
                return;
            }
            var date = info.event.start.toISOString().split('T')[0];
            window.location.href = '/sc/add_daily_intake/' + date + '/';
        },

        events: function (fetchInfo, successCallback, failureCallback) {
            console.log('Fetching events from', fetchInfo.start, 'to', fetchInfo.end);
            // イベントを取得
            axios.post('/sc/list/', {
                start_date: fetchInfo.start.getTime(),
                end_date: fetchInfo.end.getTime()
            })
            .then(function(response) {
                var events = response.data;
                console.log('Events:', events);
                // 日次摂取も取得
                axios.post('/sc/daily_intakes/', {
                    start_date: fetchInfo.start.getTime(),
                    end_date: fetchInfo.end.getTime()
                })
                .then(function(response2) {
                    var intakes = response2.data;
                    console.log('Intakes:', intakes);
                    var allEvents = events.concat(intakes);
                    console.log('All events:', allEvents);
                    successCallback(allEvents);
                })
                .catch(function(error) {
                    console.error('Error fetching intakes:', error);
                    successCallback(events);
                });
            })
            .catch(function(error) {
                console.error('Error fetching events:', error);
                failureCallback(error);
            });
        },
    });

    calendar.render();
    console.log('Calendar rendered with locale:', calendar.getOption('locale'));
});