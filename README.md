# Timetable Manager
## Note
**Currently the program only supports Russian language as the language of interface**
[Перейти на русский](https://github.com/YaNesyTortiK/TimetableManager/blob/main/README.ru-RU.md)

* [About](#about)
* [Download and run](#download-and-run)
    - [Download for linux](#download-for-linux)
        - [via Docker (recommended)](#install-via-docker-recommended)
        - [Install using the source code](#install-using-source-code)
    - [Install for windows](#install-for-windows)
* [Initial setup](#initial-setup)
    - [Enter the settings](#enter-the-settings)
    - [After initial setup](#after-initial-setup)
* [Settings](#settings)
    - [Server settings](#server-settings)
    - [Data settings](#data-settings)
    - [Iframe settings](#iframe-settings)
    - [Grouping and render settings](#grouping-and-render-settings)
    - [Bells settings](#bells-settings)
    - [Mutation settings](#mutation-settings)
    - [Carousel settings](#carousel-settings)
    - [Carousel redactor](#carousel-redactor)
* [Additional functions](#additional-functions)
    - [Update file on server](#update-file-on-server)
    - [Upload file](#upload-file)
    - [Custom Iframe](#custom-iframe)
* [Tools](#tools)
    - [Log management](#log-management)
    - [Data management](#data-management)
    - [Server Management Tools](#server-management-tools)
        - [Change password](#password-change)
        - [Create custom function](#create-a-custom-function)
        - [Remove custom function](#remove-custom-function)
        - [Delete all timetable files](#delete-all-schedule-files)
        - [Delete old timetable files](#delete-old-schedule-files)
    - [Information](#information)
* [Usage](#using-the-program-in-schedule-display-mode)
    - [Overview](#overview)
    - [Kiosk mode](#setting-kiosk-mode-for-windows-recommended-for-interactivetouch-panels)

## About
This project is a web server program for storing, updating and displaying schedules. To view the schedule, it is recommended to use an interactive (touch) panel or computer (The program interface is not optimized for devices with small screens (tablets, phones)). To run the program, it is recommended to use an independent computer/virtual machine/server with the Linux Ubuntu 22.04 LTS operating system. You can also use computers with the Windows operating system to get basic understanding about the program's functionality and test it.

![Overview](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Overview.png?raw=true)

# Download and run
## Download for Linux
It is recommended to use Ubuntu 22.04 LTS as the operating system (The following instructions will be written for this system)
### Install via Docker (recommended)
1. Update apt
```
sudo apt update
sudo apt upgrade -y
```
2. Install dependencies
```
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
```
3. Add Docker repositories
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
4. Install Docker
```
sudo apt update
sudo apt install docker-ce -y
```
5. Check the installation
```
sudo systemctl status docker
```
After executing this command you should see that docker successfully started and running.

6. Enable Docker autostart (on server reboot)
```
sudo systemctl enable docker
```
7. Check the installation
```
sudo docker run hello-world
```
This command will install a test image and run it in a docker container. If there are no errors during the startup process and you see a welcome message from Docker, then the installation was successful.

8. Download and start docker image (Instead of `-e TZ="Etc/UTC"` set your time zone, example for Moscow: `-e TZ="Europe/Moscow"`)
```
sudo docker run -d --name=TimetableManager -p 80:5000 --restart unless-stopped -e TZ="UTC" ghcr.io/yanesytortik/timetable-manager:latest
```
After the image is downloaded and launched, you can [go to page](http://127.0.0.1). f everything was successful, a web page should load that says `Ошибка соединения: Internal server Error. Something happened during getting data. Error: Сервер настроен неправильно или не настроен. Свяжитесь с системным администратором`. After this, you can proceed to [initial server setup](#initial-setup)
![InitialCfgRequired](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/InitialCfgRequired.png?raw=true)

### Install using source code
This method is suitable for those who know how to administer Linux servers.
1. Download the source code from the repository
2. Check that your python version **__is not lower than 3.11__** (otherwise the code will throw an error)
3. Create virtual environment
```
python3 -m venv venv
```
4. Activate environment
```
source venv/bin/activate
```
5. Install dependencies
```
pip3 install -r requirements.txt
```
6. Start server for testing
```
gunicorn --bind 0.0.0.0:80 wsgi:app
```
After entering this command, if everything went well, you will be able to go to the address [127.0.0.1](http://127.0.0.1) or to the address of your computer on the local network.

7. Stop the test server using a keyboard shortcut Ctrl+C.

Next setup will use an option for automatic startup using systemd. If you want to use nginx, you don't have to follow the instructions below.

8. Create a bash script to start automatically
```
echo "gunicorn --bind 0.0.0.0:80 wsgi:app" > startup.sh
```
9. Add the ability to run a script (if it was created without this parameter)
```
chmod +x startup.sh
```
10. Check by running the script with the command
```
./startup.sh
```
If the program has started and you can log into the server, stop execution.

11. Create a service to autostart when the system starts.
```
sudo nano /etc/systemd/system/timetable.service
```
Inside the file, write the following, replacing "\<path to file\>" with the path to the startup.sh script
```
[Unit]
Description=Timetable Manager
After=network.target
[Service]
ExecStart=<path to file>
[Install]
WantedBy=default.target
```
Save (Ctrl+O) and exit the editor (Ctrl+X)

12. Restart systemctl
```
sudo systemctl daemon-reload
```
13. Set the service to autostart
```
sudo systemctl enable timetable.service
```
14. Start the service
```
sudo systemctl start timetable.service
```

## Install for Windows
ATTENTION, this method is not stable and it is not recommended to use it in a real situation. You can use it for testing.
1. Install python3.11 from [https://www.python.org/downloads/release/python-3114/](https://www.python.org/downloads/release/python-3114/). Make sure that the "Add to PATH" button was pressed during installation.
2. Download the code from the repository
3. Create a virtual environment in the folder with files
```
python -m venv venv
```
4. Activate the virtual environment
```
venv/Scripts/Activate
```
(If an error occurs, run the following commands in turn: `cd venv`, `cd Scripts`, `./Activate`, `cd ..`, `cd ..`)

5. Install Dependencies
```
pip install -r requirements.txt
```
6. Run by command
```
python wsgi.py
```
After this, you can go to the address [127.0.0.1:5000](127.0.0.1:5000) and check that everything started successfully.

7. To stop the server, use the keyboard shortcut Ctrl+C

# Initial setup
### Enter the settings
1. Go to [127.0.0.1/config/](http://127.0.0.1/config/) (If you are running the program with `python wsgi.py`: [127.0.0.1:5000/config/](http: //127.0.0.1:5000/config/)). After this, the message “Не авторизованы. Войти” will appear. Click on the link "Войти" (http://127.0.0.1/login/) (If you run the program using `python wsgi.py`: "Войти" (http://127.0.0.1:5000/login/)) and you should see a page with input fields for "User" and "Password"
![Login](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Login.png?raw=true)
2. Enter your details. (If you are logging in for the first time, by default your login information is: `User: admin`, `Password: admin`)

### After initial setup
> ATTENTION
> After the initial setup, be sure to change your password [How to change the password](#password-change)

1. Save all changes by clicking the "Save" button in the lower right corner of the page.
2. Reboot the server. Required after the initial setup; then a reboot is required if any settings are not applied automatically. If you are using docker use the following commands:
    - List running applications
    ```
    sudo docker ps 
    ```
    - Restart the application using its container id (first 3 characters) (Example `fe2`)
    ```
    sudo docker restart <id>
    ```

# Settings
### Server Settings
> ATTENTION
> It is not recommended to change these settings if you are using Docker or gunicorn to run the program


![ServerSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/ServerSettings.png?raw=true)
1. IP адрес - server address (default 0.0.0.0). If you run the program using `python wsgi.py`, the server can be accessed at two addresses: `127.0.0.1` and your local network address. If you run the program using Docker or gunicorn, this setting will not affect the address
2. Порт - server port (default 5000). If you run the program using `python wsgi.py`, then to access the page you will need to specify the port (example: `127.0.0.1:5000/config/` to access the configuration page). **If you are using Docker, this setting should remain unchanged**.
3. Отладка - enable debugging mode (disabled by default). Affects the behavior of the program if an unexpected error occurs. **Recommended for testing purposes only**.
4. Файл для логов - a file where actions related to server management and errors that occur will be recorded (by default `log.txt`). Sometimes you will need to clear the logs to prevent using too much disk space. [Log management](#log-management)
5. output logs to the console (disabled by default). Duplicates the information written in log file to the console.
6. Экспорт настроек - (Export settings) when you click the button, a pop-up window with text will open. Copy this text and save it to a text file or send it as is without changes. <b>Please note that passwords and logins are NOT exported.</b>
7. Импорт настроек - (Import settings) when you click the button, a pop-up window will open with a text input field. Copy the text that you received when exporting the settings, paste it into the text field and click on the send button. If you see the line `Успешно! Перезагрузите сервер.` This means the settings have been successfully loaded and applied. It is recommended to restart the server. <b>Please note that passwords and logins are NOT imported.</b>

### Data Settings
![DataSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/DataSettings.png?raw=true)
1. Директория с таблицей - folder/directory where all excel/libre office tables with schedules are stored (by default `data/timetable/`). It is recommended to use an absolute path to specify the directory (Windows: `C:\Users\user\timetable\` Linux: `/mnt/timetable/`). **__If you are using Docker DO NOT change this setting__**
2. Время жизни данных - how often the data will be forced to refresh from the table (default 3600 sec). If you only use table loading via the web interface, you can set the value to `0` to disable forced updating.

### Iframe settings
iframe - embedded html document. Used to embed schedules on external sites. You can try generation using [Custom Iframe](#custom-iframe)
![IframeSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/IframeSettings.png?raw=true)
1. Сохранять и генерировать iframe - generate and save iframe(default is off). If this option is disabled, the following settings have no effect.
2. Путь сохранения файла - where the generated file will be saved (by default `index.html`). It is recommended to use an absolute path to specify the directory (Windows: `C:\Users\user\iframes\iframe.html` Linux: `/mnt/iframes/iframe.html`). **__If you are using Docker DO NOT change this setting__**
3. Количество колонок в таблице - Number of columns in the table (default 5). (Example: if a schedule is generated for 6 classes, then 5 classes will be in the first row of the table and the last one will go to the second row, first column)
4. Количество дней в таблице - Number of days in the table. For how many days the schedule will be generated in the iframe (default 2). Please note that the first day will be the current day, so in order to generate a schedule for the next day, specify 2 in this field. Also, the program does not take into account weekends (days that are not allocated for output ([Grouping and display settings](#grouping-and-render-settings))), so if, for example, Saturday and Sunday are not allocated for display and the schedule will be generated on Friday for 2 days, then the iframe will have a schedule for Friday and Monday.
5. Дополнительный header для iframe - Additional header for iframe. Additional data to be written in the head of the iframe file in the form of html code (empty by default). For example, you can add additional styles for table elements. Example:
```
.timetable {
    // Style for the table itself
}
.table_item {
    // Table for one class
}
.name {
    // Style for class name
}
.lesson {
    // Style for the line itself containing a separate lesson
    // ATTENTION, the lesson line color is set using the color in the Excel/Libre Office table
}
```

### Grouping and render settings
![RenderSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/RenderSettings.png?raw=true)
1. Какие параллели(группы отображать) - Which parallels (groups) to display. The program will display and add to the iframe only those parallels (groups) that are specified in this field (by default 5;6). Parallels (groups) are written separated by `;` (semicolon). (Example: 5;6;7) (Read below for how groups are generated)

2. Вторая смена (Second Shift)
    - Сдвиг смены - Shift shift. How many table rows are skipped when processing classes (groups) on the second shift (default 6). (Example: If you need to move the 6th grade to the second shift, move their lessons in the Excel/Libre Office table to the specified number. If the first lesson of the second shift begins on the 7th lesson of the first, specify the shift `6` and move the first lesson of the desired parallel to Lesson 7 of the first shift in the table)
    - Параллели на второй смене - Parallels on the second shift. Which parallels (groups) are on the second shift (default 6). Parallels (groups) are written separated by `;` (semicolon). (Example: 5;6;7) (Read below for how groups are generated)
3. Параллели(группы) - Parallels (groups). By default, all parallels (groups) are generated automatically. The program takes all the classes indicated in the table and divides them into groups, the group is formed from classes whose names without the last character match. (Example: "5a", "5b" will be in group "5", "6a", "6b" will be in group "6", but "6ab" will be in group "6a"). If you want to add a group manually, click on "+". Two input forms will appear, on the left - the name of the group, on the right - the classes that are contained in this group (Example: group - 6, class - 6a; 6b; 6ab. In this case, “6ab” will be in group “6”). If a class is added to any group manually, it will be skipped during automatic distribution. (To delete a group, press "X")
4. Вывод дней - which days will be displayed (default: Пн, Вт, Ср, Чт, Пт (English: Mon, Tue, Wed, Thu, Fri )). **These names must exactly match what is in the table**

### Bells Settings
![BellsSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/BellsSettings.png?raw=true)

If a bell schedule is added, a bell button is added to the class selection menu; when clicked, the schedule is displayed. The program also highlights the next lesson for the current day or the current lesson.

By default, calls are not installed. To add a call schedule, click on the "Add group" button. An element with the following settings will appear:

- Расписание на - (Schedule for) what type of schedule is installed (by default - all days). Allows you to set different schedules for days of the week and specific dates.
- Удалить группу - (Delete group) permanently deletes the group.
- Выберите день недели (if the “day of the week” schedule is selected) - (Select the day of the week) indicate the days of the week for which the schedule will be valid.
- Укажите дату (if the schedule for “date” is selected) - specify the date (by clicking on the element and selecting the day in the calendar) for which the schedule will be applied.

Below (under the separating line) you can create a schedule.
To add a lesson to the schedule, click "+", to delete "X"

Forms to fill out:
* Lesson number
* Start of lesson - Hour: Minute (in 24 hour format. Example: 08:05)
* End of lesson - Hour: Minute (in 24 hour format. Example: 09:45)
* Комментарий - comment on the break after the lesson (Example: Dining room)

For the second shift schedule, continue counting from the first lesson of the second shift. (Example: shift shift - 6 lessons, in this case for the first lesson of the second shift use the number "7")

Schedule priority:
- Higher (always used if available) - schedule for the date.
- Medium (used if there is no schedule for the date) - schedule for the day of the week.
- Lowest (used if there is no schedule for a date or day of the week) - all days.
- Absent (if the schedule is not specified) - the “Звонки” button will be absent on the bottom panel and the next and current lessons will not be highlighted.

### Mutation Settings
![MutationSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/MutationSettings.png?raw=true)
1. Расширенные названия - Expanded Titles. Titles that will be displayed when you click on the class schedule. Example: Math - Mathematics (On the left is what is indicated in the table with the schedule, on the right is what will be displayed.) ("+" for adding, "x" for deleting)
2. C;fnst yfpdfybz - Compressed titles. Titles that will be displayed in general form (parallel view) and in an iframe. Example: Literature - LIT (On the left is what is indicated in the table with the schedule, on the right is what will be displayed.) ("+" for adding, "x" for deleting)

### Carousel settings
![CarouselSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CarouselSettings.png?raw=true)

1. Включить карусель - (enable carousel) Enables the carousel feature (disabled by default). On the parallel schedule selection panel (bottom of main screen), a “Карусель” button will appear; when clicked, the carousel interface will open.
![CarouselInterface](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CarouselInterface.png?raw=true)

    * The image will be resized to fit the interface (while maintaining the aspect ratio)
    * To go to the next picture, click on the right side of the picture (if the interactive carousel is activated)
    * To go to the previous picture, click on the left side of the picture (if the interactive carousel is activated)
    * To exit the interface, click on the dark part around (or anywhere if the interactive carousel is activated)

2. Директория с файлами - (directory with files) the folder where all the pictures that will be shown are stored (by default `data/carousel/`).

3. Автоматическая активация через _ секунд - (Automatic activation after _ seconds) after how many seconds of inactivity (no user clicks on the screen) will the carousel automatically turn on (Default `900`). To disable automatic activation, enter the value `0`

4. Автоматическая прокрутка через _ секунд - (Auto scroll after _ seconds) after how many seconds of inactivity with the carousel activated (the interface is visible) will it automatically switch to the next picture (Default `15`). To disable automatic scrolling, enter a value of `0`. (If the picture is switched manually, the timer will be reset)

5. Разрешить на мобильных устройствах - (Allow on mobile devices) whether the carousel will be enabled on mobile devices (Disabled by default). (A mobile device will be considered a device that has: '.*Android.*|.*webOS.*|.*iPhone.*|.*iPad.*|.*iPod.*|.*BlackBerry. *|.*IEMobile.*|.*Opera Mini.*' in the request header (recognition function: `server.py:utility_processor`)). It is recommended to disable this option to reduce the load on the network and device.

6. Интерактивная карусель - enables interactivity (enabled by default). Enables the ability to interact with the display of media files in the carousel interface. When this option is disabled, the interface does not have the ability to list through files and the interface closes with any click.

7. Редактор карусели - (Carousel editor) link to [redactor interface](#carousel-redactor)

### Carousel redactor
![CarouselRedactor](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CarouselRedactor.png?raw=true)

1. Загруженный контент - (Uploaded content) all uploaded files are presented here

    * To download the file, click on the name under the picture
    * To delete a file, click the "Удалить" button (Deleted files are beyond retrieve)

2. Загрузить - (Upload) field for uploadinf files

    * Supported file formats: 
        * Images: 'png', 'jpeg', 'jpg', 'webp', 'gif' (`tools:storage.py:Carousel:image_extension`)
        * Videos: 'mp4', 'webm', 'ogv', 'ogg' (`tools:storage.py:Carousel:video_extension`)
    * It is possible to upload multiple files at the same time

Note! If you upload a video, it will play WITHOUT SOUND! Also, if the video duration exceeds the set time for auto-switching, this time will automatically extend to the video duration. If the video duration is less than the set switching time, the video will play in a circle until automatic switching occurs.

# Additional functions
Additional features can only be used after initial setup
### Update file on server
The button to the right of the "Settings" button. Force file update and iframe creation (if enabled). When you click the button, another tab will open with information about the update.
Example of a successful file update:
`Глобальное расписание успешно загружено из файла "data/timetable/01_01_2000.xlsx".`

### Upload file
![UploadFile](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/UploadFile.png?raw=true)
The button to the right of the "Update file on server" button. A function for downloading a table with a schedule via the web interface (it is recommended to use it as the main method, since during the download process the file is checked for compliance with the parser requirements). When you click the button, a page will open with a gray area for uploading files by dragging or selecting in Explorer (when clicked). The file must have the extension .xls, .xlsx or .ods and be named day-month-year.extension (Example: 01-01-2000.xlsx). After selecting the file, click the send button. If everything went well, a green message will appear `Файл успешно загружен, данные успешно обновлены.`. If an error occurs, a red message will appear indicating the reason for the error.

### Custom Iframe
The button to the right of the "Загрузить файл" button. Function for generating iframes with additional parameters (even if generating and saving iframes is disabled in the settings)
![CustomIframe](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CustomIframe.png?raw=true)
1. Количество дней в таблице - Number of days in the table. For how many days the schedule will be generated in the iframe (default 2). Please note that the first day will be the current day, so in order to generate a schedule for the next day, specify 2 in this field. Also, the program does not take into account weekends (days that are not allocated for output ([Grouping and render settings](#grouping-and-render-settings))), so if, for example, Saturday and Sunday are not allocated for display and the schedule will be generated on Friday for 2 days, then the iframe will have a schedule for Friday and Monday.
2. Количество столбцов в таблице - Number of columns in the table (default 5). (Example: if a schedule is generated for 6 classes, then 5 classes will be in the first row of the table and the last one will go to the second row, first column).
3. Пропуск дней - Skip days. How many **working** days should be missed. Please note that the current day is also considered a working day (see point 1), therefore, in order to generate a schedule for example for the day after tomorrow (considering that this is a working day), you need to specify the skipping days `2` (today and tomorrow).
4. Сгенерировать и сохранить iframe - Generate and save iframe (Available only if the "Generate and save iframe" function is enabled) - generates and saves an iframe in the location specified in the settings.

5. Сгенерировать iframe - Generate iframe. Will open an additional tab in the browser with an iframe generated based on the entered settings (to add additional styles, change the “Additional header” parameter in [iframe settings](#iframe-settings)). (This function will NOT save the file)
6. Скачать iframe - will generate and save an iframe file to your computer according to the specified settings.

# Tools
To access the toolbar, click the button next to the "Выйти" (Logout) button
![Tools](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Tools.png?raw=true)
### Log management
1. Скачать лог - download a file with logs as a .txt file
2. Последние 100 строк лога - when clicked, an additional tab will open with the last 100 lines from the log file
3. Очистить лог - clears the log file completely

### Data management
1. Скачать данные - download the table with the current schedule
2. Скачать данный в формате json - Download data in json format - current data in .json format (for debugging)
3. Скачать пример данных - download a table with an example of organizing data to display a schedule. (This data is used during the first launch)

## Server Management Tools
ATTENTION. If you use these tools carelessly, you can make unauthorized changes to the source code of the program and disable it or lose data.

### Password Change
1. Go to [configuration page](http://127.0.0.1/config/) (enter login information if required).

2. In the upper right corner of the screen, click the "Инструменты" (Tools) button (Next to the "Выйти" (Logout) button)


3. In the pop-up window that appears, find the “Сменить пароль” (Change password) button (In the “Управление” (Management) group).
![ChangePassword](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/ChangePassword.png?raw=true)
4. In the form that opens, enter your current password in the "Текущий пароль" field. In the "Новый пароль" (new password) and "Повторите" (repeat) fields, enter your new password and click "Сменить пароль" (Change password).

5. Repeat the login procedure using a new password ([How to enter settings](#enter-the-settings))

### Create a custom function
Used to write custom scripts to automate certain processes.
![CustomFunction](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CustomFunction.png?raw=true)
1. When you click the button, a page with data entry fields will open:
    - Имя функции - Function name - how the function will be displayed in the additional functions panel (will be added to the right of the "Custom Iframe" button)
    - Описание - Description (optional)
    - Консольная команда - Console command - script to execute. The script is written in a language supported by the operating system (Docker uses bash, Windows uses batch)
2. To load the script, click the corresponding button and your function will appear in the additional functions panel (top)
3. When you click on the button responsible for launching this function, a pop-up window will appear with information about the completion of the script or an error during execution.

### Remove custom function
(Available only if there is at least one custom function)
When clicked, a page with buttons will open. When you click the button, the corresponding function will be deleted **beyond retrieve**.

### Delete all schedule files
When clicked, all tables are deleted. (When updating the data, the server will report an error and continue working on the previously used data)

### Delete old schedule files
(Available only if there are at least two files in the directory with tables)
When clicked, all unused tables are deleted.
(The table used is the table with the larger date in the file name)

## Information
- Github репозиторий - link to this repo (https://github.com/YaNesyTortiK/TimetableManager)
- Документация - link to the README on russian
- Сообщить об ошибке - link to issues page on this repo
- Информация о сервере - will show basic info about program (Name, version, modification, when version saved, contact info)
- Серверное время - server time, will open a page with server time (to update data reload page)

# Using the program in schedule display mode
### Overview
1. In order to enter the interface, go to the IP address of the server on the local network (Example: 192.168.0.15) (If you started the server on Windows, do not forget to specify port 5000 (Example: "192.168.0.15:5000")).

2. When you log in, you will see a page with the following content.

![Overview](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Overview.png?raw=true)

- At the top of the page there is a clock and a calendar
- The schedule itself is located in the middle
- At the bottom there are buttons for switching active parallels/groups, as well as a “Teachers” button with automatically generated teacher schedules.
- Also, if you have entered a call schedule in the settings ([Call Schedule](#bells-settings)), the "Calls" button will be displayed to display the call schedule.

### Setting "kiosk mode" for Windows (recommended for interactive/touch panels)
Please note that this may not be possible on all versions of Windows.
Detailed instructions for creating a kiosk mode account can be found on [the official microsoft page](https://learn.microsoft.com/en-en/windows/configuration/assigned-access/quickstart-kiosk?tabs=settings)

## License
Timetable Manager. Web-server to manage, store and distribute timetable on local network with simple and easy to understand design. 
Copyright (C) 2024  YaNesyTortik

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact info: github.com/YaNesyTortik/TimetableManager
