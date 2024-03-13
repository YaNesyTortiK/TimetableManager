const save_iframe_base_url = '/save_iframe/'
const gen_iframe_base_url = '/generate_iframe/'
const download_iframe_base_url = '/download_iframe/'

const days_inp = document.getElementById('days')
const columns_inp = document.getElementById('columns')
const skip_inp = document.getElementById('skip')

const popup_container = document.getElementsByClassName('popup_container')[0];

function gen() {
    let url = gen_iframe_base_url+days_inp.value+'/'+columns_inp.value+'/'+skip_inp.value+'/'
    window.open(url, '_blank')
}

function download() {
    let url = download_iframe_base_url+days_inp.value+'/'+columns_inp.value+'/'+skip_inp.value+'/'
    window.open(url, '_blank')
}

function gen_n_save() {
    let url = save_iframe_base_url+days_inp.value+'/'+columns_inp.value+'/'+skip_inp.value+'/'
    fetch(url)
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
