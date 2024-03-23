import json

class Config:
    is_setup = False # Была ли проведена первоначальная настройка
    use_web_editor = False # Использовать редактор через веб-интерфейс (если нет, то используется xlsx файлы с изменениями)
    
    debug = False # Отладка
    host = '127.0.0.1' # (Если запуск через wsgi.py) Хост сервера (Должен соответствовать ip адресу компьютера, либо локальному)
    port = 5000 # (Если запуск через wsgi.py) Порт сервера (Не должен конфликтовать с другими открытыми портами)

    username = "admin" # Имя пользователя для входа в систему конфигурации
    password = "admin" # Пароль для пользователя
    
    initial_file = False # Если используется веб-редактор, то файл будет содержать шаблонные данные
    directory = 'data\\timetable\\'  # Директория (папка) с файлами расписания (если не используется веб-редактор) (Должно заканчиваться на \\ для виндовс и / для других)
    
    lifetime = 300 # Время жизни кеша данных (Обновление данных произойдет в случае, если с послежнего запроса прошло больше, чем заданное время) в секундах
    save_iframe = False # Сохранять расписание на сегодня-завтра как отдельный html файл
    iframe_file = "iframe.html" # Путь и имя iframe файла (html код с расписанием на сегодня-завтра)
    second_shift = [] # Какие параллели выведены на вторую смену (Прим: ['5', '6'])
    second_shift_delay = 6 # Через какое количество уроков первой смены начинается вторая (Прим: Если вторая смена начинается с 7 урока первой, то значение будет 6)
    groups = {} # Принудительное разделение на группы. Пример: {'Тест группа': ['5а', '6а', '7а'], ...} Нераспределенные по группам классы распределятся автоматически основываясь на значение до последнего символа (5а - параллель 5, 11а - параллель 11, 11аб - параллель 11а)
    show = [] # Какие параллели показывать (если в файле содержаться младшие классы, для которых не следует выводить расписание) (Прим: ['5', '6'])
    days = ["Пн", "Вт", "Ср", "Чт", "Пт"] # Какие дни недели показывать (Должно соответствовать названиям дней недели в первом столбце файла с расписанием)
    iframe_columns = 5 # Количество колонок в таблице iframe
    iframe_days = 2 # Количества дней для вывода в iframe
    short = { # Данные для сокращения уроков. Используется для сокращения названий предметов для удобного вывода на экран в общей таблице. (Заполнение не обязательно)
        # Первый параметр - как предмет записан в таблице, Второй параметр - на что заменять
        # Пример использования:
        # "Математика": "Мат"
    }
    full = { # Данные для полного названия предметов (Заполнение не обязательно)
        # Первый параметр - как предмет записан в таблице, Второй параметр - полное имя предмета для вывода полноценной информации для одного класса
        # Пример использования:
        # "Русск. яз.": "Русский язык"
    }
    weekdays_short = { # (Заполнение не обязательно)
        # Если в первом столбце таблицы записаны сокращенные названия дней недели, для вывода полной информации рекомендуется изменить на полные
        # Пример:
        # "Пн": "Понедельник",
    }
    custom_functions = { # Дополнительные функции для расширения функционала программы
        # Имя: {
        #   "description": Описание,
        #   "cmd": Команда которая будет запущена по нажатию на кнопку.   
        #   }
    }
    bells = { # Расписание звонков для подсветки текущего (следующего после перемены) урока
        # номер урока: [начало урока, конец урока, доп.информация о перемене после урока]
        # Пример: 
        # "1": ["8:00", "8:40", None],
        # "2": ["8:50", "9:30", "Завтрак 1-е классы"]
        # Если словарь пустой, никакие уроки подсвечиваться не будут
    }
    log_filename = 'log.txt' # Файл для записи логов
    log_to_console = False # Писать логи в консоль
    funfunct = True

    custom_iframe_head = '' # Кастомный текст для head при генерации iframe

    program_info = {
        'name': 'Timetable Manager',
        'version': '1.2.7',
        'modification': 'Stable',
        'saved': '23.03.2024 23:41 UTC+3',
        'contact_info': 'https://github.com/YaNesyTortiK/TimetableManager'
    }

    def __init__(self, file: str) -> None:
        self.file = file
        self._parse_file() # Запуск функции парсинга данных
    
    def _parse_file(self):
        try:
            with open(self.file, 'r', encoding='utf-8') as f: # Открытие файла через контекстный менеджер
                data = json.load(f) # Загрузка данных из json формата в dict формат питона
                for k in data.keys(): # Перебор параметров по ключу
                    setattr(self, k, data[k]) # Установка атрибута класса с соответствующим значением
        except FileNotFoundError:
            self.write_config() # Создаем файл если он не найден

    def write_config_from_dict(self, data):
        for key, value in data.items():
            if key == 'custom_iframe_head':
                print('CCC', value)
            if key not in ['password', 'username', 'program_info', 'custom_functions'] and value != None:
                if key == 'initial_file':
                    setattr(self, key, '.\\schemas\\'+value)
                else:
                    setattr(self, key, value)
        if not self.is_setup: # Если впервые изменена конфигурация
            self.is_setup = True
        self.write_config()

    def write_config(self):
        data = {
            "is_setup": self.is_setup,
            "use_web_editor": self.use_web_editor,
            "schema_file": self.initial_file,
            "directory": self.directory,
            "lifetime": self.lifetime,
            "host": self.host,
            "port": self.port,

            "username": self.username,
            "password": self.password,

            "debug": self.debug,
            "second_shift": self.second_shift,
            "second_shift_delay": self.second_shift_delay,
            "show": self.show,
            "groups": self.groups,
            "days": self.days,
            "save_iframe": self.save_iframe,
            "iframe_file": self.iframe_file,
            "iframe_columns": self.iframe_columns,
            "iframe_days": self.iframe_days,
            "weekdays_short": self.weekdays_short,

            "short": self.short,
            "full": self.full,
            "custom_functions": self.custom_functions,
            "bells": self.bells,
            "log_filename": self.log_filename,
            "log_to_console": self.log_to_console,
            "custom_iframe_head": self.custom_iframe_head,
            "funfunct": self.funfunct
        }
        with open(self.file, 'w', encoding='utf-8') as f: # Открытие файла через контекстный менеджер
            data = json.dump(data, f) # Загрузка данных из json формата в dict формат питона
