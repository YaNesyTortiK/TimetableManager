const carousel_url = '/carousel/'
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
    let data = await load_carousel_data(t);
    if (data.type.includes('image')) {
        let image = new Image()
        image.src = URL.createObjectURL(data)
        image.classList.add('carousel_elem')
        carousel.innerHTML = ''
        carousel.appendChild(image)
    }
    if (next_timeout !== undefined) {
        clearTimeout(next_timeout)
    }
    if (carousel_delay > 0) {
        next_timeout = setTimeout(update_carousel, carousel_delay*1000)
    }
}

async function load_carousel_data(t) {
    if (t === 'init'){
        current = await fetch(carousel_url)
            .then((response)=>{return response.json().then((r)=>{return r['file']})})
        return fetch(carousel_url+current+'/')
            .then((response)=>{return response.blob().then((r)=>{return r})})
    } else if (t === 'prev') {
        current = await fetch(carousel_url, {
            method: "POST",
            body: JSON.stringify({
                "step": -1,
                "current": current
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then((response)=>{return response.json().then((r)=>{return r['file']})})
        return fetch(carousel_url+current+'/')
            .then((response)=>{return response.blob().then((r)=>{return r})})
    } else {
        current = await fetch(carousel_url, {
            method: "POST",
            body: JSON.stringify({
                "step": 1,
                "current": current
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then((response)=>{return response.json().then((r)=>{return r['file']})})
        return fetch(carousel_url+current+'/')
            .then((response)=>{return response.blob().then((r)=>{return r})})
    }
}

function carousel_closed() {
    if (next_timeout !== undefined) {
        clearTimeout(next_timeout)
        next_timeout = undefined
    }
}