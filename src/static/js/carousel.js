const carousel_url = '/carousel/'
const blobs_url = '/carousel/blob/'
const image_types = ['png', 'jpeg', 'jpg', 'webp', 'gif']
const video_types = ['mp4', 'webm', 'ogv']
let current = undefined
let next_timeout = undefined;

function show_carousel() {
    if (document.getElementById('carousel_data') !== null) return;
    popup_container.innerHTML = `<div class="popup__bg" onclick="close_popup(this); carousel_closed();"><div class="carousel_popup" onclick="this.classList.add('clicked')">
<button class="inline_elem carousel_arrow left" onclick="update_carousel('prev')"><</button>
<div class="inline_elem" id="carousel_data"></div>
<button class="inline_elem carousel_arrow right" onclick="update_carousel()">></button>
    </div></div>`;
    popupBg = popup_container.children[0];
    popup = popupBg.children[0];
    popupBg.classList.add('active');
    popup.classList.add('active');
    update_carousel('init')
    if (next_timeout !== undefined) {
        clearTimeout(next_timeout)
    }
    if (carousel_delay > 0) {
        next_timeout = setTimeout(update_carousel, carousel_delay*1000)
    }
}

async function update_carousel(t) {
    let carousel = document.getElementById('carousel_data')
    if (carousel == null) return;
    let file = await load_carousel_data(t);
    if (image_types.includes(file.slice(file.lastIndexOf('.')+1))) {
        carousel.innerHTML = `<img class="carousel_elem" src="${blobs_url+file+'/'}">`
        if (next_timeout !== undefined) {
            clearTimeout(next_timeout)
        }
        if (carousel_delay > 0) {
            next_timeout = setTimeout(update_carousel, carousel_delay*1000)
        }
    } else if (video_types.includes(file.slice(file.lastIndexOf('.')+1))) {
        carousel.innerHTML = `<video class="carousel_elem" src="${blobs_url+file+'/'}" autoplay muted loop>Браузер не поддерживает проигрывание видео :(</video>`
        let vid = carousel.getElementsByClassName('carousel_elem')[0]
        vid.addEventListener('loadeddata', ()=>{
            if (next_timeout !== undefined) {
                clearTimeout(next_timeout)
            }
            if (carousel_delay > 0) {
                if (vid.duration < carousel_delay) {
                    next_timeout = setTimeout(update_carousel, carousel_delay*1000)
                } else {
                    next_timeout = setTimeout(update_carousel, vid.duration*1000)
                }
            }
        })
    } else {
        update_carousel('next');
    }
}

async function load_carousel_data(t) {
    if (t === 'init'){
        return await fetch(carousel_url)
            .then((response)=>{return response.json().then((r)=>{current = r['file']; return r['file']})})
    } else if (t === 'prev') {
        return await fetch(carousel_url, {
            method: "POST",
            body: JSON.stringify({
                "step": -1,
                "current": current
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then((response)=>{return response.json().then((r)=>{current = r['file']; return r['file']})})
    } else {
        return await fetch(carousel_url, {
            method: "POST",
            body: JSON.stringify({
                "step": 1,
                "current": current
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then((response)=>{return response.json().then((r)=>{current = r['file']; return r['file']})})
    }
}

function carousel_closed() {
    if (next_timeout !== undefined) {
        clearTimeout(next_timeout)
        next_timeout = undefined
    }
}