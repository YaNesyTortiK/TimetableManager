const maxWidth = 250;
const minWidth = 110;

window.addEventListener('resize', () => {
    update_size() ;
 });

function update_size() {
    const rows = document.getElementsByClassName('row');
    const teacher_rows = document.getElementsByClassName('teacher_row');
    const buttons = document.getElementsByClassName('overlay_button');
    const glob_time = document.getElementById('global_timetable')
    let coDays = null; let coKlasses = null;
    try {
        coDays = parseInt(rows[0].id.toString().split(' ')[0]);
        coKlasses = parseInt(rows[0].id.toString().split(' ')[1]);
    } catch (ex) {}
    try {
        coDays = parseInt(teacher_rows[0].id.toString().split(' ')[0]);
        coKlasses = parseInt(teacher_rows[0].id.toString().split(' ')[1]);
    } catch (ex) {}
    let newHeight = (parseFloat(timetable_container.offsetHeight)/coDays-15).toString()+'px';
    let newWidth = (parseFloat(timetable_container.offsetWidth)/coKlasses-15);
    if (newWidth > maxWidth) {
        newWidth = maxWidth.toString()+'px';
    } else if (newWidth < minWidth) {
        newWidth = minWidth.toString()+'px';
        glob_time.style.justifyContent = 'left';
    } else {
        newWidth = newWidth.toString()+'px';
        glob_time.style.justifyContent = 'center';
    }
    for (let element of rows){
        element.style.minHeight = newHeight;
        element.style.width = newWidth;
    }
    for (let element of teacher_rows){
        element.style.min_height = newHeight;
    }
    for (let element of buttons){
        element.style.height = newHeight
        element.style.width = newWidth
    }
}
