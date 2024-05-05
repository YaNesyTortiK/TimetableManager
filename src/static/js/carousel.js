const carousel_url = '/carousel/'
let current = undefined

function show_carousel() {
    popup_container.innerHTML = `<div class="popup__bg" onclick="close_popup(this)"><div class="carousel_popup" onclick="this.classList.add('clicked')">
<button class="inline_elem carousel_arrow left" onclick="update_carousel('prev')"><</button>
<div class="inline_elem" id="carousel_data"></div>
<button class="inline_elem carousel_arrow right" onclick="update_carousel()">></button>
    </div></div>`;
    popupBg = popup_container.children[0];
    popup = popupBg.children[0];
    popupBg.classList.add('active');
    popup.classList.add('active');
    update_carousel('init')
}

async function update_carousel(t) {
    let data = await load_carousel_data(t);
    let carousel = document.getElementById('carousel_data')
    if (data.type.includes('image')) {
        let image = new Image()
        image.src = URL.createObjectURL(data)
        image.classList.add('carousel_elem')
        carousel.innerHTML = ''
        carousel.appendChild(image)
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