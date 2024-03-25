# Timetable Manager

* [О программе](#о-программе)
* [Установка и запуск](#установка-и-запуск)
    - [Установка для Linux](#установка-для-linux)
        - [Через Docker (рекомендуется)](#установка-с-помощью-docker-рекомендуется)
        - [С использованием исходного кода](#с-использованием-исходного-кода)
    - [Установка для Windows](#установка-для-windows)
* [Первоначальная настройка](#первоначальная-настройка)
    - [Вход в настройки](#вход-в-настройки)
    - [После первоначальной настройки](#после-первоначальной-настройки)
* [Настройка](#настройка)
    - [Настройка сервера](#настройка-сервера)
    - [Настройка данных](#настройка-данных)
    - [Настройка iframe](#настройка-iframe)
    - [Настройка группировки и отображения](#настройка-группировки-и-отображения)
    - [Расписание звонков](#расписание-звонков)
    - [Настройка преобразований](#настройка-преобразований)
* [Дополнительные функции](#дополнительные-функции)
    - [Обновить файл на сервере](#обновить-файл-на-сервере)
    - [Загрузить файл](#загрузить-файл)
    - [Custom Iframe](#custom-iframe)
* [Инструменты](#инструменты)
    - [Управление логами](#управление-логами)
    - [Управление данными](#управление-данными)
    - [Инструменты управления сервером](#инструменты-управления-сервером)
        - [Смена пароля](#смена-пароля)
        - [Создать кастомную функцию](#создать-кастомную-функцию)
        - [Удалить кастомную функцию](#удалить-кастомную-функцию)
        - [Удалить старые файлы с расписанием](#удалить-старые-файлы-с-расписанием)
* [Использование](#использование-программы-в-режиме-показа-расписания)
    - [Обзор](#обзор)
    - [Режим киоска](#установка-режима-киоска-для-windows-рекомендуется-для-интерактивныхсенсорных-панелей)

## О программе
Данный проект представляет собой программу-веб сервер для хранения, обновления и отображения расписания. Для просмотра расписания рекомендуется использовать интерактивную (сенсорную) панель или компьютер (Интерфейс программы не оптимизирован для устройств с маленькими экранами (планшеты, телефоны)). Для запуска программы рекомендуется использовать независимый компьютер/виртуальную машину/сервер с операционной системой Linux Ubuntu 22.04 LTS. Вы можете также использовать компьютеры с операционной системой Windows для ознакомления с функционалом программы и тестирования.

![Overview](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Overview.png?raw=true)

# Установка и запуск
## Установка для Linux
В качестве операционной системы рекомендуется использовать Ubuntu 22.04 LTS (Следуюшие инструкции будут написаны для данной системы)
### Установка с помощью Docker (рекомендуется)
1. Обновите пакетный менеджер
```
sudo apt update
sudo apt upgrade -y
```
2. Установите требуемые зависимости
```
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
```
3. Добавление репозиториев Docker
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
4. Установка Docker
```
sudo apt update
sudo apt install docker-ce -y
```
5. Проверьте установку
```
sudo systemctl status docker
```
После выполнения этой команды вы должны увидеть что docker успешно запущен и работает.

6. Включение автозапуска Docker (Автозапуск программы при перезгрузке сервера)
```
sudo systemctl enable docker
```
7. Проверьте правильность установки
```
sudo docker run hello-world
```
Данная команды установит тестовый образ и запустит его в docker контейнере. Если в процессе запуска не вывелось каких-либо ошибок и вы увидели приветственное сообщение от Docker, в таком случае установка прошла успешно.

8. Загрузите и запустите образ 
```
sudo docker run -d --name=TimetableManager -p 80:5000 --restart unless-stopped ghcr.io/yanesytortik/timetable-manager:latest
```
После того как образ будет загружен и запущен вы можете [перейти на страницу](http://127.0.0.1). Если все выполнилось успешно, должна загрузится веб-страница с надписью `Ошибка соединения: Internal server Error. Something happened during getting data. Error: Сервер настроен неправильно или не настроен. Свяжитесь с системным администратором`. После этого вы можете переходить к [первоначальной настройке сервера](#первоначальная-настройка)
![InitialCfgRequired](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/InitialCfgRequired.png?raw=true)


### С использованием исходного кода
Данный способ подходит тем, кто умеет администрировать linux сервера.
1. Скачайте исходный код из репозитория
2. Проверьте что ваша версия python **__не ниже 3.11__** (в противном случае код будет выдавать ошибку)
3. Создайте виртуальное окружение
```
python3 -m venv venv
```
4. Активируйте окружение
```
source venv/bin/activate
```
5. Установите зависимости
```
pip3 install -r requirements.txt
```
6. Запустите сервер для проверки
```
gunicorn --bind 0.0.0.0:80 wsgi:app
```
После ввода этой команды, если все прошло успешно, вы сможете перейти по адресу [127.0.0.1](http://127.0.0.1) или по адресу вашего компьютера в локальной сети.

7. Остановите тестовый сервер с помощью сочетания клавиш Ctrl+C.

Далее будет представлен вариант автоматического запуска с использованием systemd. Если вы хотите использовать nginx, вы можете не следовать дальнейшим инструкциям.

8. Создайте bash скрипт для автоматического запуска
```
echo "gunicorn --bind 0.0.0.0:80 wsgi:app" > startup.sh
```
9. Добавьте возможность запускать скрипт (если он был создан без этого параметра)
```
chmod +x startup.sh
```
10. Проверьте правильность запустив скрипт командой 
```
./startup.sh
```
Если программа запустилась и вы можете зайти на сервер остановите выполнение.

11. Создайте сервис для автозапуска при старте системы.
```
sudo nano /etc/systemd/system/timetable.service
```
Внутри файла пропишите следующее, заменив "<путь к файлу>" на путь до скрипта startup.sh
```
[Unit]
Description=Timetable Manager
After=network.target
[Service]
ExecStart=<путь к файлу>
[Install]
WantedBy=default.target
```
Сохраните (Ctrl+O) и выйдите из редактора (Ctrl+X)

12. Перезагрузите systemctl
```
sudo systemctl daemon-reload
```
13. Установите сервис в автозапуск
```
sudo systemctl enable timetable.service
```
14. Запустите сервис
```
sudo systemctl start timetable.service
```

## Установка для Windows
ВНИМАНИЕ, данный способ не стабилен и не рекомендуется использовать его в реальной ситуации. Вы можете использовать его для тестирования.
1. Установите python3.11 с сайта [https://www.python.org/downloads/release/python-3114/](https://www.python.org/downloads/release/python-3114/). Убедитесь что во время установки была нажата кнопка "Add to PATH"
2. Скачайте код из репозитория
3. Создайте виртуальное окружение в папке с файлами
```
python -m venv venv
```
4. Активируйте виртуальное окружение
```
venv/Scripts/Activate
```
(Если возникает ошибка по очереди выполните следующие команды: `cd venv`, `cd Scripts`, `./Activate`, `cd ..`, `cd ..`)

5. Установите зависимости
```
pip install -r requirements.txt
```
6. Запустите код командой
```
python wsgi.py
```
После этого вы сможете перейти по адресу [127.0.0.1:5000](127.0.0.1:5000) и проверить что все запущено успешно.

7. Для остановки сервера воспользуйтесь сочетанием клавиш Ctrl+C

# Первоначальная настройка
### Вход в настройки
1. Перейдите по адресу [127.0.0.1/config/](http://127.0.0.1/config/) (Если вы запускаете программу с помощью `python wsgi.py`: [127.0.0.1:5000/config/](http://127.0.0.1:5000/config/)). После этого появится надпись `Не авторизованы. Вход`, нажмите на ссылку [Вход](http://127.0.0.1/login/) (Если вы запускаете программу с помощью `python wsgi.py`: [Вход](http://127.0.0.1:5000/login/)) и вы должны увидеть страницу с полями для ввода "Пользователь" и "Пароль"
![Login](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Login.png?raw=true)
2. Введите ваши данные. (Если вы заходите в первый раз, по умолчанию ваши данные для входа: `Пользователь: admin`, `Пароль: admin`)

### После первоначальной настройки
> ВНИМАНИЕ
> После первоначальной настройки обязательно измените свой пароль [Как сменить пароль](#смена-пароля)
1. Сохраните все изменения нажатием кнопки "Сохранить" в правом нижнем углу страницы.
2. Перезагрузите сервер. Обязательно после первоначальной настройки, далее перезагрузка требуется, если какие-либо настройки не применились автоматически. Если вы используете docker воспользуйтесь следующими командами:
    - Выведите список запущенных приложений
    ```
    sudo docker ps 
    ```
    - Перезапустите приложение с помощью его container id (первые 3 символа) (Пример `fe2`)
    ```
    sudo docker restart <id>
    ```

# Настройка
### Настройка сервера
> ВНИМАНИЕ
> Не рекомендуется изменять эти настройки если вы используете Docker или gunicorn для запуска программы

![ServerSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/ServerSettings.png?raw=true)
1. IP адрес - адрес сервера (по умолчанию 0.0.0.0). Если вы запускаете программу с помощью `python wsgi.py`, доступ к серверу можно получить по двум адресам: `127.0.0.1` и ваш адрес в локальной сети. Если вы запускаете программу с помощью Docker или gunicorn данная настройка не повлияет на адрес
2. Порт - порт сервера (по умолчанию 5000). Если вы запускаете программу с помощью `python wsgi.py`, то для доступа к странице понадобится указывать порт (прим: `127.0.0.1:5000/config/` для доступа к странице настройки). **Если вы используете Docker, этот параметр должен оставаться без изменений**.
3. Отладка - включить режим отладки (по умолчанию выключено). Влияет на поведение программы в случае возникновения непредвиденной ошибки. **Рекомендуется использовать только для тестирования**.
4. Файл для логов - файл куда будут записываться действия связанные с управлением сервера и возникающими ошибками (по умолчанию `log.txt`). Иногда потребуется очищать логи, для предотвращения использования слишком большого количества места на диске. [Управление логами](#управление-логами)
5. Писать логи в консоль - вывод логов в консоль (по умолчанию выключено). Дублирует информацию записываемую в файл для логов в консоль.

### Настройка данных
![DataSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/DataSettings.png?raw=true)
1. Директория с таблицей - папка/директория где хранятся все excel/libre office таблицы с расписанием (по умолчанию `data/timetable/`). Рекомендуется использовать абсолютный путь для указания директории (Windows: `C:\Users\user\timetable\` Linux: `/mnt/timetable/`). **__Если вы используете Docker НЕ изменяйте этот параметр__**
2. Время жизни данных - как часто данные будут принудительно обновлены из таблицы (по умолчанию 300 сек.). Если вы используете только загрузку таблицы через веб-интерфейс, вы можете установить значение `0`, чтобы отключить принудительное обновление.

### Настройка iframe
iframe - встраиваемый html документ. Используется для встраивания расписания на внешние сайты. Вы можете попробовать генерацию с помощью [Custom Iframe](#custom-iframe)
![IframeSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/IframeSettings.png?raw=true)
1. Сохранять и генерировать iframe - (по умолчанию выключено), если этот параметр отключен, следующие настройки не вносят изменения.
2. Путь сохранения файла - куда будет сохранен сгенерированный файл (по умолчанию `index.html`). Рекомендуется использовать абсолютный путь для указания директории (Windows: `C:\Users\user\iframes\iframe.html` Linux: `/mnt/iframes/iframe.html`). **__Если вы используете Docker НЕ изменяйте этот параметр__**
3. Количество колонок в таблице - (по умолчанию 5) (Пример: если генерируется расписание для 6 классов, то 5 классов будут в первой строке таблицы и последний перейдет во вторую строку, первый столбец)
4. Количество дней в таблице - на сколько дней будет сгенерировано расписание в iframe (по умолчанию 2). Обратите внимание, что первый день будет текущим днем, поэтому для того, чтобы генерировать расписание на следующий день, укажите в этом поле 2. Также программа не учитывает выходные (дни которые не выделены для вывода ([Настройки группировки и отображения](#настройка-группировки-и-отображения))), поэтому, если, к примеру, суббота и воскресенье не выделены для отображения и расписание будет генерироваться в пятницу на 2 дня, тогда в iframe будет расписание на пятницу и понедельник.
5. Дополнительный header для iframe - дополнительные данные для записи в head iframe файла в виде html кода (по умолчанию пусто). К примеру вы можете добавить дополнительные стили для элементов таблицы. Пример: 
```
.timetable {
    // Стиль для самой таблицы
}
.table_item {
    // Таблица для одного класса
}
.name {
    // Стиль для имени класса
}
.lesson {
    // Стиль для самой строки содержайщей отдельный урок
    // ВНИМАНИЕ, цвет строки урока задается с помощью цвета в таблице Excel/Libre Office
}
```

### Настройка группировки и отображения
![RenderSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/RenderSettings.png?raw=true)
1. Какие параллели(группы отображать) - программа будет выводить на экран и добавлять в iframe только те параллели(группы) которые указаны в этом поле (по умолчанию 5;6). Параллели(группы) записываются разделяя `;`(точка с запятой). (Пример: 5;6;7) (Как генерируются группы читайте ниже)
2. Вторая смена
    - Сдвиг смены - сколько строк таблицы пропускается при обработке классов(групп) на второй смене (по умолчанию 6). (Пример: Если нужно перевести 6-е классы на вторую смену, переместите их уроки в таблице Excel/Libre Office на указанное число. Если первый урок второй смены начинается на 7 уроке первой, укажите сдвиг `6` и переместите первый урок нужной параллели на 7 урок первой смены в таблице)
    - Параллели на второй смене - какие параллели(группы) на второй смене (по умолчанию 6). Параллели(группы) записываются разделяя `;`(точка с запятой). (Пример: 5;6;7) (Как генерируются группы читайте ниже)
3. Параллели(группы) - по умолчанию все параллели(группы) генерируются автоматически. Программа берет все классы указанные в таблице и разделяет их по группам, группа формируется из классов, имена(названия) которых без последнего символа совпажают. (Пример: "5а", "5б" попадут в группу "5", "6а", "6б" попадут в группу "6", однако "6аб" попадет в группу "6а"). Если вы хотите добавить группу вручную, нажмите на "+". Появятся две формы для ввода, слева - название группы, справа - классы которые содержатся в этой группе (Пример: группа - 6, класс - 6а;6б;6аб. В таком случае "6аб" окажется в группе "6"). Если класс добавлен в какую-либо группу вручную, он будет пропущен при автоматическом распределении. (Для удаления группы нажмите "Х")
4. Вывод дней - какие дни будут отображаться (по умолчанию: Пн, Вт, Ср, Чт, Пт). **Данные названия должны в точности совпадать с тем, что находится в таблице**

### Расписание звонков
![BellsSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/BellsSettings.png?raw=true)
Если добавлено расписание звонков, в меню выбора классов добавляется кнопка звонки, при нажатии на которую выводится расписание. Также программа подсвечивает следующий урок на текущий день или текущий урок.
Для добавления урока в расписание нажмите "+", для удаления "Х"

Формы для заполнения:
* Номер урока
* Начало урока - Час:Минута (в 24 часовом формате. Пример: 08:05)
* Конец урока - Час:Минута (в 24 часовом формате. Пример: 09:45)
* Комментарий - комментарий к перемене после урока (Пример: Столовая)

Для расписания второй смены продолжайте счет с первого урока второй смены. (Пример: сдвиг смены - 6 уроков, в таком случае для первого урока второй смены используйте цифру "7") 

### Настройка преобразований
![MutationSettings](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/MutationSettings.png?raw=true)
1. Расширенные названия - Названия, которые будут выводиться при нажатии на расписание класса. Пример: Мат - Математика (Слева - то, что указано в таблице с расписанием, справа, то, что будет выведено.) ("+" для добавления, "х" для удаления)
2. Сжатые названия - Названия, которые будут выводиться в общем виде (вид параллели) и в iframe. Пример: Литература - ЛИТ (Слева - то, что указано в таблице с расписанием, справа, то, что будет выведено.) ("+" для добавления, "х" для удаления)


# Дополнительные функции
Дополнительные функции могут быть использованы только после первоначальной настройки
### Обновить файл на сервере
Кнопка справа от кнопки "Настройка". Принудительное обновление файла и создание iframe (если включено). При нажатии на кнопку откроется еще одна вкладка с информацией об обновлении.
Пример успешного обновления файла: 
`Глобальное расписание успешно загружено из файла "data/timetable/01_01_2000.xlsx".`

### Загрузить файл
![UploadFile](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/UploadFile.png?raw=true)
Кнопка справа от кнопки "Обновить файл на сервере". Функция для загрузки таблицы с расписанием через веб-интерфейс (рекомендуется использовать в качестве основного способа, так как в процессе загрузки файл проходит проверку на соответствие требованиям парсера). При нажатии на кнопку откроется страница с серой областью для загрузки файлов перетаскиванием или выбором в проводнике (при нажатии). Файл должен быть с расширением .xls, .xlsx или .ods и называться день-месяц-год.расширение (Пример: 01-01-2000.xlsx). После выбора файла нажмите кнопку отправить. Если все прошло успешно появится зеленая надпись `Файл успешно загружен, данные успешно обновлены.`. В случае ошибки появится красная надпись с причиной ошибки.

### Custom Iframe
Кнопка справа от кнопки "Загрузить файл". Функция для генерации iframe с дополнительными параметрами (даже если генерация и сохранение iframe в настройках выключены)
![CustomIframe](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CustomIframe.png?raw=true)
1. Количество дней в таблице - на сколько дней будет сгенерировано расписание в iframe (по умолчанию 2). Обратите внимание, что первый день будет текущим днем, поэтому для того, чтобы генерировать расписание на следующий день, укажите в этом поле 2. Также программа не учитывает выходные (дни которые не выделены для вывода ([Настройки группировки и отображения](#настройка-группировки-и-отображения))), поэтому, если, к примеру, суббота и воскресенье не выделены для отображения и расписание будет генерироваться в пятницу на 2 дня, тогда в iframe будет расписание на пятницу и понедельник.
2. Количество столбцов в таблице - (по умолчанию 5) (Пример: если генерируется расписание для 6 классов, то 5 классов будут в первой строке таблицы и последний перейдет во вторую строку, первый столбец).
3. Пропуск дней - сколько **рабочих** дней следует пропустить. Обратите внимание, что текущий день также считается за рабочий (см. п.1), поэтому, чтобы сгенерировать расписание например на послезавтра (учитывая что это рабочий день), нужно указать пропуск дней `2` (сегодня и завтра).
4. Сгенерировать и сохранить iframe (Доступно только если включена функция "Генерировать и сохранять iframe") - генерирует и сохраняет iframe в указанном в настройках месте.
5. Сгенерировать iframe - откроет дополнительную вкладку в браузере со сгенерированным по введенным настройкам iframe (для того чтобы добавить дополнительные стили измените параметр "Дополнительный header" в [Настройка iframe](#настройка-iframe)). (Данная функция НЕ сохранит файл)
6. Скачать iframe - сгенерирует и сохранит на ваш компьютер файл iframe по заданным настройкам. 

# Инструменты
Для доступа к панели инструментов нажмите кнопку рядом с кнопкой "Выйти"
![Tools](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Tools.png?raw=true)
### Управление логами
1. Скачать лог - скачать файл с логами в виде .txt файла
2. Последние 100 строк лога - при нажатии откроется дополнительная вкладка с последними 100 строками из файла с логами
3. Очистить лог - очищает файл лога полностью

### Управление данными
1. Скачать данные - скачать таблицу с текущим расписанием
2. Скачать данный в формате json - текущие данные в .json формате (для отладки)
3. Скачать пример данных - скачать таблицу с примером организации данных для вывода расписания. (При первом запуске используются эти данные)

## Инструменты управления сервером
ВНИМАНИЕ. При неаккуратном использовани данных инструментов вы можете внести несанкционированные изменения в исходный код программы и вывести её из строя либо потерять данные.

### Смена пароля
1. Перейдите на [страницу настройки](http://127.0.0.1/config/) (введите данные для входа если нужно).

2. В верхнем правом углу экрана нажмите кнопку "Инструменты" (Рядом с кнопкой "Выход")

3. В появившемся всплывающем окне найдите кнопку "Сменить пароль" (В группе "Управление").
![ChangePassword](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/ChangePassword.png?raw=true)
4. В открывшейся форме введите текущий пароль в поле "Текущий пароль". В поля "Новый пароль" и "Повторите" введите ваш новый пароль и нажмите изменить пароль.

5. Повторите процедуру входа используя новый пароль ([Как войти в настройки](#вход-в-настройки))

### Создать кастомную функцию
Используется для написания пользовательских скриптов для автоматизации некоторых процессов.
![CustomFunction](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/CustomFunction.png?raw=true)
1. При нажатии на кнопку откроется страница с полями ввода данных:
    - Имя функции - то как функция будет отображаться на панели дополнительных функций (будет добавлена справа от кнопки "Custom Iframe")
    - Описание (необязательно)
    - Консольная команда - скрипт для выполнения. Скрипт пишется на языке поддерживаемом операционной системой (Docker использует bash, Windows - batch)
2. Для загрузки скрипта нажмите соответствующую кнопку и ваша функция появится на панели дополнительных функций (сверху)
3. При нажатии на кнопку отвечающую за запуск данной функции появится всплывающее окно с информацией о завершении скрипта или об ошибке во время исполнения.

### Удалить кастомную функцию
(Доступно только если есть хотя-бы одна кастомная функция)
При нажатии откроется страница с кнопками. При нажатии на кнопку соответствующая функция будет **безвозвратно** удалена.

### Удалить старые файлы с расписанием
(Доступно только если есть не менее двух файлов в директории с таблицами)
При нажатии удаляются все неиспользуемые таблицы.
(Используемая таблица - таблица с бОльшей датой в названии файла)

# Использование программы в режиме показа расписания
### Обзор
1. Для того чтобы зайти в интерфейс, прейдите по ip адресу сервера в локальной сети (Пример: 192.168.0.15) (Если вы запустили сервер на windows, не забудьте указать порт 5000 (Пример: "192.168.0.15:5000")).

2. При входе перед вами появится страница со следующим содержанием.

![Картинка](https://github.com/YaNesyTortiK/MyGlobalAssets/blob/main/Overview.png?raw=true)

- Вверху страницы расположены часы, и календарь
- По середине расположено само расписание
- Снизу расположены кнопки переключения активных параллелей/групп, а также кнопка "Учителя" с автоматически сгенерированными расписаниями учителей.
- Также, если вы ввели расписание звонков в настройках ([Расписание звонков](#расписание-звонков)), будет отображаться кнопка "Звонки" для вывода расписания звонков.

### Установка "режима киоска" для Windows (рекомендуется для интерактивных/сенсорных панелей)
Обратите внимание, что не на всех версиях Windows это возможно сделать.
Подробную инструкцию по созданию учетной записи режима киоска вы можете найти на [официальной странице microsoft](https://learn.microsoft.com/ru-ru/windows/configuration/assigned-access/quickstart-kiosk?tabs=settings)

## Лицензия
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