const parallel_url = '/get_rendered_parallel/';
const popup_url = '/popup/';
const timetable_container = document.getElementById('timetable_container');
const popup_container = document.getElementsByClassName('popup_container')[0];
const teachers_url = '/teachers/';
const teacher_popup_url = '/teacher_popup/';
const bells_url = '/bells/'
const bells_container = document.getElementById("show_bells_btn")

const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
let clcks = 0;
let currently_loaded = undefined;
let carousel = false;
let carousel_after = undefined;
let carousel_delay = undefined;
let delay_carousel_timeout = undefined;

function load_parallel(elem) {
    let num = elem.name;
    currently_loaded = num;
    fetch(parallel_url, {
        method: 'POST',
        body: JSON.stringify(
            {
                'num': num
            }
        ),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response=>{
            if (response.ok) 
                response.text().then(data=>{timetable_container.innerHTML = data; update_size(); check_ongoing();});
            else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка рендера: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}


function overlay(elem) {
    let klass = elem.id.split('^');
    let o_day_num = weekday_map[klass[1]];
    currently_loaded = o_day_num;
    fetch(popup_url, {
        method: 'POST',
        body: JSON.stringify(
            {
                klass: klass[0],
                day: klass[1]
            }
        ),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response=>{
            if (response.ok) {
                response.text().then(data=>{
                    popup_container.innerHTML = data;
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                    if (typeof(bells) !== "undefined") {
                        highlight_lesson_in_popup(o_day_num);
                    }
                })
            } else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка рендера: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}

function load_teachers() {
    fetch(teachers_url)
        .then(response=>{
            if (response.ok) 
                response.text().then(data=>{timetable_container.innerHTML = data; update_size();});
            else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка рендера: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}

function load_teacher(elem) {
    let teacher = elem.id;
    fetch(teachers_url, {
        method: 'POST',
        body: JSON.stringify(
            {
                teacher: teacher
            }
        ),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response=>{
            if (response.ok) 
                response.text().then(data=>{timetable_container.innerHTML = data; update_size();});
            else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка рендера: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}

function teacher_popup(elem) {
    let data = elem.id.split('^')
    fetch(teacher_popup_url, {
        method: 'POST',
        body: JSON.stringify(
            {
                teacher: data[0],
                day: data[1]
            }
        ),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response=>{
            if (response.ok) {
                response.text().then(data=>{
                    popup_container.innerHTML = data;
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            } else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка рендера: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}

function close_popup(elem) {
    if (!elem.children[0].classList.contains('clicked')) {
        elem.classList.remove('active'); // Убираем активный класс с фона
        elem.children[0].classList.remove('active'); // И с окна
        elem.innerHTML = ''
    } else {
        elem.children[0].classList.remove('clicked');
    }
}

function get_info() {
    if (clcks > 6) {
        clcks = 0;
        popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h2 class="klass_title">Информация о сервере</h2>'+document.getElementById('program_info').innerHTML+'</div></div>';
        popupBg = popup_container.children[0];
        popup = popupBg.children[0];
        popupBg.classList.add('active');
        popup.classList.add('active');
    } else {
        clcks = clcks+1;
    }
}

function load_startup() {
    const parallel = document.getElementsByClassName('parallel_btn')[0];
    load_parallel(parallel);
}

function load_bells() {
    fetch(bells_url)
        .then(response=>response.json().then(data=>{
            for (temp in data) {
                bells=data;
                bells_container.style = "";
                break;
            }
            }))
        .catch()
}

function show_bells() {
    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h2 class="klass_title">Расписание звонков</h2>'+document.getElementById('bells_table').innerHTML+'</div></div>';
    popupBg = popup_container.children[0];
    popup = popupBg.children[0];
    popupBg.classList.add('active');
    popup.classList.add('active');
}

function highlight_lesson_in_popup() {
    let tbl = document.getElementsByClassName('in_popup')[0];
    let o_day_num = weekdays.indexOf(tbl.getAttribute('day_num'));
    if (typeof(current_lesson) === "undefined")
        return;
    if (o_day_num != current_lesson[2])
        return;
    if (!tbl.parentElement.classList.contains('active'))
        return;
    for (lsn of tbl.getElementsByTagName('tr')) {
        if (lsn.getAttribute('true_num') == current_lesson[0] && lsn.getAttribute('true_num') !== '') {
            if (current_lesson[1]) {
                lsn.classList.add('ongoing_lesson')
                lsn.classList.remove('next_lesson')
            } else {
                lsn.classList.add('next_lesson')
                lsn.classList.remove('ongoing_lesson')
            }
        } else {
            lsn.classList.remove('ongoing_lesson')
            lsn.classList.remove('next_lesson')
        }
    }
}

function clean_highlight(day_num) {
    let rasp_cells = undefined;
    // ckean highlight on bells timetable
    rasp_cells = document.getElementsByClassName('bells_table_inner')
    for (elem in rasp_cells) {
        if (typeof(rasp_cells[elem]) !== 'object')
            break
        let lesson_cells = rasp_cells[elem].getElementsByClassName('__lesson_cell')
        for (lesson in lesson_cells) {
            if (typeof(lesson_cells[lesson]) !== 'object')
                break
            lesson_cells[lesson].classList.remove('next_lesson');
            lesson_cells[lesson].classList.remove('ongoing_lesson'); 
        }
    }
    // clean highlights in body
    let row = timetable_container.getElementsByTagName('tbody')[0]
    if (typeof(row) == 'undefined') {
        return;
    }
    row = row.getElementsByClassName('row');
    if (typeof(row) == 'undefined') {
        return;
    }
    row = row[day_num]
    if (typeof(row) == 'undefined') {
        return;
    }
    rasp_cells = row.getElementsByClassName("__rasp_cell")
    for (elem in rasp_cells) {
        if (typeof(rasp_cells[elem]) !== 'object')
            break
        let lesson_cells = rasp_cells[elem].getElementsByClassName('__lesson_cell')
        for (lesson in lesson_cells) {
            if (typeof(lesson_cells[lesson]) !== 'object')
                break
            lesson_cells[lesson].classList.remove('next_lesson');
            lesson_cells[lesson].classList.remove('ongoing_lesson');
        }
    }
}

function highlight_lesson(lesson_num, day_num, currently) {
    let rasp_cells = undefined;
    // highlight on bells timetable
    rasp_cells = document.getElementsByClassName('bells_table_inner')
    for (elem in rasp_cells) {
        if (typeof(rasp_cells[elem]) !== 'object')
            break
        let lesson_cells = rasp_cells[elem].getElementsByClassName('__lesson_cell')
        for (lesson in lesson_cells) {
            if (typeof(lesson_cells[lesson]) !== 'object')
                break
            lesson_cells[lesson].classList.remove('next_lesson');
            lesson_cells[lesson].classList.remove('ongoing_lesson');
            if (lesson_cells[lesson].getAttribute('true_num') == lesson_num && !lesson_cells[lesson].classList.contains('ongoing_lesson')) {
                if (currently) {
                    lesson_cells[lesson].classList.add('ongoing_lesson');
                } else {
                    lesson_cells[lesson].classList.add('next_lesson');
                }
            }  
        }
    }

    // highlight on global timetable
    let row = timetable_container.getElementsByTagName('tbody')[0]
    if (typeof(row) == 'undefined') {
        return;
    }
    row = row.getElementsByClassName('row');
    if (typeof(row) == 'undefined') {
        return;
    }
    row = row[day_num]
    if (typeof(row) == 'undefined') {
        return;
    }
    rasp_cells = row.getElementsByClassName("__rasp_cell")
    for (elem in rasp_cells) {
        if (typeof(rasp_cells[elem]) !== 'object')
            break
        let lesson_cells = rasp_cells[elem].getElementsByClassName('__lesson_cell')
        for (lesson in lesson_cells) {
            if (typeof(lesson_cells[lesson]) !== 'object')
                break
            lesson_cells[lesson].classList.remove('next_lesson');
            lesson_cells[lesson].classList.remove('ongoing_lesson');
            if (lesson_cells[lesson].getAttribute('true_num') == lesson_num && !lesson_cells[lesson].classList.contains('ongoing_lesson') && lesson_cells[lesson].getAttribute('true_num') !== '') {
                if (currently) {
                    lesson_cells[lesson].classList.add('ongoing_lesson');
                } else {
                    lesson_cells[lesson].classList.add('next_lesson');
                }
            }  
        }
    }
}

function check_sync_time() {
    fetch('/time/')
        .then(response=>response.text().then(data=>{
            const server = new Date(data)
            const client = new Date()
            // Приемлимая разница во времени - 3 минуты
            if ((server >= client && (server-client)/1000/60>3) || (server < client && (client-server)/1000/60>3)) {
                popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h2 class="klass_title">Предупреждение!</h2><p>Серверное время не совпадает с временем на устройстве! Это может вызвать некорректную работу и отображение!</p>'+`<span><b>Серверное время:</b> ${server}</span><br><span><b>Локальное время:</b> ${client}</span>`+'</div></div>';
                popupBg = popup_container.children[0];
                popup = popupBg.children[0];
                popupBg.classList.add('active');
                popup.classList.add('active');
            }
            }))
        .catch()
}

function delay_daily_restart() {
    let now = new Date();
    let millis = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 5, 0, 0) - now;
    if (millis < 0) {
        millis += 86400000;
    }
    setTimeout(function(){window.location.reload()}, millis);
}

function load_carousel_cfg() {
    let cont = document.getElementById('carousel_config')
    let data = JSON.parse(cont.innerHTML.toLowerCase())
    carousel = data['carousel']
    carousel_after = data['carousel_after']
    carousel_delay = data['carousel_delay']
    if (carousel) {
        document.addEventListener('click', delay_carousel)
        delay_carousel()
    }
}

function delay_carousel() {
    if (delay_carousel_timeout !== undefined) clearTimeout(delay_carousel_timeout);
    delay_carousel_timeout = setTimeout(show_carousel, carousel_after*1000);
}

load_bells();
load_carousel_cfg();
load_startup();
check_sync_time();
delay_daily_restart();