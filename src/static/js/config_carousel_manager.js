const upload_url = '/carousel_edit/'
const remove_url = '/carousel_edit/remove/'

const popup_container = document.getElementsByClassName('popup_container')[0]

function remove_carousel_image(elem) {
    fetch(remove_url+elem.id)
        .then(response=>{
            if (response.ok) 
                window.location.reload();
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
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}

function upload_image(elem) {
    let data = new FormData()
    for (file of elem.files) {
        data.append('file', file)
    }
    fetch(upload_url, {
        method: 'POST',
        body: data
    })
        .then(response=>{
            if (response.ok) 
                window.location.reload();
            else {
                response.text().then(error=>{
                    popup_container.innerHTML = '<div class="popup__bg" onclick="window.location.reload();"><div class="popup">Ошибка соединения: '+error.toString()+'</div></div>';
                    popupBg = popup_container.children[0];
                    popup = popupBg.children[0];
                    popupBg.classList.add('active');
                    popup.classList.add('active');
                })
            }
        })
        .catch((error) => {
            popup_container.innerHTML = '<div class="popup__bg" onclick="close_popup(this)"><div class="popup">Ошибка загрузки: '+error.toString()+'</div></div>';
            popupBg = popup_container.children[0];
            popup = popupBg.children[0];
            popupBg.classList.add('active');
            popup.classList.add('active');
        })
}