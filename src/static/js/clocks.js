let bells = undefined;
let last_greater = false;

let month = document.querySelector(".month");
let day = document.querySelector(".day");
let year = document.querySelector(".year");
let months = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь",
    "Ноябрь", "Декабрь"
];
const day_map = { // set zero day as Monday
  0: 6,
  1: 0,
  2: 1,
  3: 2,
  4: 3,
  5: 4,
  6: 5,
}

const weekday_map = { // set zero day as Monday
  'Вс': 6,
  'Пн': 0,
  'Вт': 1,
  'Ср': 2,
  'Чт': 3,
  'Пт': 4,
  'Сб': 5,
}

let current_lesson = undefined;

function clockTimer() {
  var date = new Date();

  var time = [date.getHours(),date.getMinutes(),date.getSeconds()]; // |[0] = Hours| |[1] = Minutes| |[2] = Seconds|
  var dayOfWeek = ["Воскресенье","Понедельник","Вторник","Среда","Четверг","Пятница","Суббота"]
  var days = date.getDay();

  if(time[0] < 10){time[0] = "0"+ time[0];}
  if(time[1] < 10){time[1] = "0"+ time[1];}
  if(time[2] < 10){time[2] = "0"+ time[2];}
  
  var current_time = [time[0],time[1],time[2]].join(':');
  var clock = document.getElementById("clock");
  var wday = document.getElementById("dayOfWeek");
  
  clock.textContent = current_time;
  wday.textContent = dayOfWeek[days];

  month.textContent = months[date.getMonth()];
  day.textContent = date.getDate();
  year.textContent = date.getFullYear();
  
  setTimeout("clockTimer()", 1000);
}

function minute_timer() {
  check_ongoing();
  setTimeout("minute_timer()", 15000); // 15 seconds is set to update highlight faster
}

function check_ongoing() {
  if (typeof(bells) !== "undefined") {
    let date = new Date();
    let hour = date.getHours();
    let minute = date.getMinutes();
    let day_num = day_map[date.getDay()];

    let cur = false;
    for (lsn in bells) {
      let temp = bells[lsn][0].split(':');
      let lsn_start_h = Number(temp[0]);
      let lsn_start_m = Number(temp[1]);
      temp = bells[lsn][1].split(':');
      let lsn_end_h = Number(temp[0]);
      let lsn_end_m = Number(temp[1]);
      
      if (lsn_start_h <= hour && lsn_end_h >= hour) {
        if (lsn_start_h !== lsn_end_h) {
          if ((hour == lsn_end_h && minute < lsn_end_m) || (hour == lsn_start_h && minute >= lsn_start_m)) {
            // console.log('FIND 1', lsn, bells[lsn])
            current_lesson = [Number(lsn), true, day_num];
            highlight_lesson(Number(lsn), day_num, true);
            highlight_lesson_in_popup(day_num);
            cur = true;
            break;
          }
        } else {
          if (lsn_start_m <= minute && minute < lsn_end_m) {
            // console.log('FIND 2', lsn, bells[lsn])
            current_lesson = [Number(lsn), true, day_num];
            highlight_lesson(Number(lsn), day_num, true);
            highlight_lesson_in_popup(day_num);;
            cur = true;
            break;
          }
        }
      }
    }
    if (!cur) {
      for (lsn in bells) {
        let temp = bells[lsn][0].split(':');
        let lsn_start_h = Number(temp[0]);
        let lsn_start_m = Number(temp[1]);
        temp = bells[lsn][1].split(':');
        let lsn_end_h = Number(temp[0]);
        let lsn_end_m = Number(temp[1]);

        if (lsn_start_h > hour) {
          // console.log('FIND 3', lsn, bells[lsn])
          current_lesson = [Number(lsn), false, day_num];
          highlight_lesson(Number(lsn), day_num, false);
          highlight_lesson_in_popup(day_num);
          cur = true;
          break;
        } else if (lsn_start_h == hour && lsn_start_m > minute) {
          // console.log('FIND 4', lsn, bells[lsn])
          current_lesson = [Number(lsn), false, day_num];
          highlight_lesson(Number(lsn), day_num, false);
          highlight_lesson_in_popup(day_num);
          cur = true;
          break;
        }
      }
    }
  }
}

function start() {
  clockTimer();
  minute_timer();
}

document.onload = start();