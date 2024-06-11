const save_url = '/config/save_config/'
const popup_container = document.getElementsByClassName('popup_container')[0];

const ip_inp = document.getElementById('ip')
const port_inp = document.getElementById('port')
const debug_flag = document.getElementById('debug')
const web_flag = document.getElementById('use_web_editor')
const lifetime_inp = document.getElementById('lifetime')
const iframe_flag = document.getElementById('save_iframe')
const iframe_file_inp = document.getElementById('iframe_file')
const iframe_columns_inp = document.getElementById('iframe_columns')
const iframe_days_inp = document.getElementById('iframe_days')
const show_inp = document.getElementById('show')
const second_shift_delay_inp = document.getElementById('second_shift_delay')
const second_shift_inp = document.getElementById('second_shift')
const dir_inp = document.getElementById('directory')
const log_filename_inp = document.getElementById('log_filename')
const log_to_console_flag = document.getElementById('log_to_console')
const custom_iframe_head = document.getElementById('custom_head')
const carousel_flag = document.getElementById('carousel')
const carousel_directory_inp = document.getElementById('carousel_directory')
const carousel_after_inp = document.getElementById('carousel_after')
const carousel_delay_inp = document.getElementById('carousel_delay')
const carousel_mobile_flag = document.getElementById('carousel_mobile')
const carousel_interactive_flag = document.getElementById('carousel_interactive')
const parser_select = document.getElementsByName('parser_type')[0]

let edited = true;

function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function remove_group(elem) {
    elem.parentElement.parentElement.removeChild(elem.parentElement)
}

function add_group(elem) {
    const par = elem.parentElement
    par.removeChild(elem)
    par.insertAdjacentHTML('beforeend', `<div class="group_container"><input class="gr_name inline_elem""> <input class="gr_content inline_elem"> <button onclick="remove_group(this)">X</button></div><button onclick="add_group(this)">+</button>`)
}

function add_bells_group(elem) {
    const par = elem.parentElement
    par.removeChild(elem)
    par.removeChild(par.getElementsByClassName('splitter')[0])
    par.insertAdjacentHTML('beforeend', `
    <div class="cfg_elem inline_elem bells_group_container">
        <label>Расписание на: </label> 
        <select name="inp_type" class="bells_inp_type inline_elem" onchange="bells_inp_type(this)">
            <option value="all">Все дни</option>
            <option value="weekday">День недели</option>
            <option value="date">Дата</option>
        </select>
        <div class="bells_inp_param"></div>
        <button onclick="remove_group(this)">Удалить группу</button>
        <hr>
        <button onclick="add_bell(this)" class="inline_elem">+</button>
    </div>
    <div class="splitter"></div>
    <button onclick="add_bells_group(this)">Добавить группу</button>
    `)

}

function add_full(elem) {
    const par = elem.parentElement
    par.removeChild(elem)
    par.insertAdjacentHTML('beforeend', `<div class="full_container"><input class="inline_elem full_orig"> : <input class="inline_elem full_change"> <button class="inline_elem" onclick="remove_group(this)">X</button></div><button onclick="add_full(this)">+</button>`)
}

function add_short(elem) {
    const par = elem.parentElement
    par.removeChild(elem)
    par.insertAdjacentHTML('beforeend', `<div class="short_container"><input class="inline_elem short_orig"> : <input class="inline_elem short_change"> <button class="inline_elem" onclick="remove_group(this)">X</button></div><button onclick="add_short(this)">+</button>`)
}

function get_show() {
    let data = []
    for (elem of show_inp.value.split(';')) {
        if (elem !== '')
        data.push(elem)
    }
    return data
}

function get_second_shift() {
    let data = []
    for (elem of second_shift_inp.value.split(';')) {
        if (elem !== '')
        data.push(elem)
    }
    return data
}

function get_days() {
    let data = []
    for (elem of document.getElementById('days_container').children) {
        if (elem.children[0].checked) {
            data.push(elem.children[0].id)
        }
    }
    return data
}

function get_groups() {
    let data = {}
    for (let container of document.getElementsByClassName('group_container')) {
        let gr_name = container.getElementsByClassName('gr_name')[0].value
        if (!(gr_name == '' || gr_name.trim() == '')) {
            let gr_content = container.getElementsByClassName('gr_content')[0].value.split(';')
            let fixed_content = []
                for (cont of gr_content) {
                    if (cont !== '')
                    fixed_content.push(cont)
                }
            if (fixed_content.length !== 0) {
                data[gr_name] = fixed_content
            }
        }
    }
    return data
}

function get_full() {
    let data = {}
    for (container of document.getElementsByClassName('full_container')) {
        let orig = container.getElementsByClassName('full_orig')[0].value
        let change = container.getElementsByClassName('full_change')[0].value
        if (orig.trim() !== '' && change.trim() !== '')
            data[orig] = change
    }
    return data
}

function get_short() {
    let data = {}
    for (container of document.getElementsByClassName('short_container')) {
        let orig = container.getElementsByClassName('short_orig')[0].value
        let change = container.getElementsByClassName('short_change')[0].value
        if (orig.trim() !== '' && change.trim() !== '')
            data[orig] = change
    }
    return data
}

function add_bell(elem) {
    const par = elem.parentElement
    par.removeChild(elem)
    par.insertAdjacentHTML('beforeend', `<div class="bells_container"><input class="inline_elem lsn_num" type="number" placeholder="Номер урока"> <input class="inline_elem start_time" placeholder="ЧЧ:ММ"> - <input class="inline_elem end_time" placeholder="ЧЧ:ММ"> <input class="inline_elem bell_comment" placeholder="Комментарий"> <button class="inline_elem" onclick="remove_group(this)">X</button></div><button onclick="add_bell(this)">+</button>`)
}

function get_bells() {
    let res = []
    for (group of document.getElementsByClassName('bells_group_container')) {
        let inp_type = group.getElementsByClassName('bells_inp_type')[0].value
        let inp_value_container = group.getElementsByClassName('bells_inp_value')[0]
        let options = null
        if (inp_type === 'weekday') {
            options = []
            for (day_check of inp_value_container.getElementsByClassName('day_check')) {
                if (day_check.checked) {
                    options.push(day_check.id)
                }
            }
        } else if (inp_type == 'date') {
            options = inp_value_container.value
        }
        let data = {'type': inp_type, 'options': options}
        for (container of group.getElementsByClassName("bells_container")) {
            let num = container.getElementsByClassName("lsn_num")[0].value.trim()
            let start_time = container.getElementsByClassName("start_time")[0].value.trim()
            let end_time = container.getElementsByClassName("end_time")[0].value.trim()
            let comment = container.getElementsByClassName("bell_comment")[0].value.trim()
            if (num == '' || !isNumeric(num) || start_time == '' || end_time == '') {
                continue
            }
            if (!start_time.includes(':')) {
                if (start_time.includes('.'))
                    start_time = start_time.replace('.', ':');
                else if (start_time.includes('-'))
                    start_time = start_time.replace('-', ':');
                else
                    continue;
            }
            if (!end_time.includes(':')) {
                if (end_time.includes('.'))
                    end_time = end_time.replace('.', ':');
                else if (end_time.includes('-'))
                    end_time = end_time.replace('-', ':');
                else
                    continue;
            }
            let temp = start_time.split(':')
            if (!isNumeric(temp[0]) || !isNumeric(temp[1]))
                continue
            temp = end_time.split(':')
            if (!isNumeric(temp[0]) || !isNumeric(temp[1]))
                continue
    
            if (comment == '')
                comment = null
    
            data[num] = [start_time, end_time, comment];
        }
        res.push(data)
    }
    return res;
}


function save_data() {
    if (log_filename_inp.value == undefined || log_filename_inp.value.trim() == '') {
        log_filename_inp.value = 'log.txt'
    }
    let res_data = {
        'use_web_editor': web_flag.checked,
        'schema_file': null, // This version doesn't support web editing
        'directory': dir_inp.value,
        'lifetime': Number(lifetime_inp.value),
        'host': ip_inp.value,
        'port': Number(port_inp.value),
        'debug': debug_flag.checked,
        'second_shift': get_second_shift(),
        'second_shift_delay': Number(second_shift_delay_inp.value),
        'show': get_show(),
        'groups': get_groups(),
        'days': get_days(),
        'save_iframe': iframe_flag.checked,
        'iframe_file': iframe_file_inp.value,
        'iframe_columns': Number(iframe_columns_inp.value),
        'iframe_days': Number(iframe_days_inp.value),
        'short': get_short(),
        'full': get_full(),
        'bells': get_bells(),
        'log_filename': log_filename_inp.value,
        'log_to_console': log_to_console_flag.checked,
        'custom_iframe_head': custom_iframe_head.value,
        'carousel': carousel_flag.checked,
        'carousel_after': Number(carousel_after_inp.value),
        'carousel_delay': Number(carousel_delay_inp.value),
        'carousel_mobile': carousel_mobile_flag.checked,
        'carousel_directory': carousel_directory_inp.value,
        'carousel_interactive': carousel_interactive_flag.checked,
        'parser_type': parser_select.value
    }
    fetch(save_url, {
        method: 'POST',
        body: JSON.stringify(res_data),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response=>{
            if (response.ok) {
                response.text().then(data=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Успешно</h3>'+data.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                    saved();
                })
            } else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Ошибка</h3>Ошибка сервера или соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Ошибка</h3>Непредвиденная ошибка: '+error.toString()+'</div></div>';
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
    } else {
        elem.children[0].classList.remove('clicked');
    }
}

function unsaved() {
    window.onbeforeunload = function(e) {
        return 'У вас есть несохраненные изменения.'
    };
}

function saved() {
    window.onbeforeunload = null;
}

function bells_inp_type(elem) {
    val = elem.value
    inp_param_container = elem.parentElement.getElementsByClassName('bells_inp_param')[0]
    if (val == '*') {
        inp_param_container.innerHTML = ''
    } else if (val == 'weekday') {
        inp_param_container.innerHTML = `
        <label>Выберите дни недели:</label>
        <div class="bells_inp_value inline_elem">
            <p class="inline_elem">Пн:<input class="inline_elem day_check" type="checkbox" id="Пн" onchange="unsaved()"> |</p>
            <p class="inline_elem">Вт:<input class="inline_elem day_check" type="checkbox" id="Вт" onchange="unsaved()"> |</p>
            <p class="inline_elem">Ср:<input class="inline_elem day_check" type="checkbox" id="Ср" onchange="unsaved()"> |</p>
            <p class="inline_elem">Чт:<input class="inline_elem day_check" type="checkbox" id="Чт" onchange="unsaved()"> |</p>
            <p class="inline_elem">Пт:<input class="inline_elem day_check" type="checkbox" id="Пт" onchange="unsaved()"> |</p>
            <p class="inline_elem">Сб:<input class="inline_elem day_check" type="checkbox" id="Сб" onchange="unsaved()"> |</p>
            <p class="inline_elem">Вс:<input class="inline_elem day_check" type="checkbox" id="Вс" onchange="unsaved()"></p>
        </div>
        `
    } else if (val == 'date') {
        inp_param_container.innerHTML = `
        <label>Укажите дату: </label>
        <input class="bells_inp_value" type="date">
        <p><b>Обратите внимание</b>, расписание на дату будет в приоритете, даже если есть расписание на день недели или на все дни.</p>
        `
    }
}

function export_settings() {
    fetch('/cfg_settings/export/').then(response => response.text().then(
        text => {
            popup_container.innerHTML = `<div class="popup__bg" onclick="close_popup(this)"><div class="popup" onclick="this.classList.add(\'clicked\')">
                Настройки (скопируйте эти строки):
                <br>
                <textarea style="font-family: monospace; height: 40vw; width: 100%; font-size: 20px;">${text}</textarea>
            </div></div>`;
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        }
    )).catch((error) => {
        popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Ошибка</h3>Непредвиденная ошибка: '+error.toString()+'</div></div>';
        popupBg = popup_container.children[0];
        popup = popupBg.children[0];
        popupBg.classList.add('active');
        popup.classList.add('active');
    })
}

function import_settings_view() {
    popup_container.innerHTML = `<div class="popup__bg" onclick="close_popup(this)"><div class="popup" onclick="this.classList.add(\'clicked\')">
        Введите строку настроек (скопированную при экспорте):
        <textarea class="settings_area" style="font-family: monospace; height: 40vw; width: 100%; font-size: 20px;" placeholder="Введите строки"></textarea>
        <button onclick="import_settings(this)" class="tool-btn">Отправить</button>
    </div></div>`;
    popupBg = popup_container.children[0];
    popup = popupBg.children[0];
    popupBg.classList.add('active');
    popup.classList.add('active');
}
function import_settings(elem) {
    text = elem.parentElement.getElementsByClassName('settings_area')[0].value
    fetch('/cfg_settings/import/', {
        method: 'POST',
        body: JSON.stringify({
            settings: text
          }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(response => {
        if (response.ok) {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup" onclick="this.classList.add(\'clicked\')">Успешно! Перезагрузите сервер.</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        } else {
            response.text().then(text => {
                popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Ошибка</h3>Непредвиденная ошибка: '+text+'</div></div>';
                popupBg = popup_container.children[0];
                popup = popupBg.children[0];
                popupBg.classList.add('active');
                popup.classList.add('active');
            })
        }
    }).catch((error) => {
        popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup"><h3>Ошибка</h3>Непредвиденная ошибка: '+error.toString()+'</div></div>';
        popupBg = popup_container.children[0];
        popup = popupBg.children[0];
        popupBg.classList.add('active');
        popup.classList.add('active');
    })
}