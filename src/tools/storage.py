from src.tools.table_parser import parse_table, save_data_to_table
from src.tools.logger import Logger
from datetime import datetime, timedelta, time
from shutil import copy2
from os import listdir, path
from os.path import isfile, join
import re

class Storage:
    def __init__(self, config) -> None:
        self.log = Logger(config.log_filename, config.log_to_console)
        self._updated = datetime.now()
        self._config = config
        if not config.is_setup:
            self._data = {'error': f'Сервер настроен неправильно или не настроен. Свяжитесь с системным администратором.'}
        else:
            try:
                self._prepare_files()
                self._load_data()
                self._data = self.data
            except Exception as ex:
                self._data = {'error': f'Что-то пошло не так при первичной загрузке данных. Ошибка: {ex}'}
                self.log.error(f'Что-то пошло не так при первичной загрузке данных. Ошибка: {ex}')
    
    def _prepare_files(self):
        if self._config.use_web_editor and len(get_filenames(self._config.directory)) == 0:
            copy2(self._config.initial_file, 
                f"{self._config.directory}\\01_01_2000.xlsx")
        elif len(get_filenames(self._config.directory)) == 0:
            raise FileNotFoundError("Не найдены файлы с расписанием в указанной директории!")

    def _load_data(self, file: str|None = None) -> tuple[str, bool]:
        # Функция загрузки данных, возвращает текстовый результат выполнения и True если произошла ошибка
        if file: # Если файл указан
            try: # Попытка получения данных
                self._updated = datetime.now() # Обновление даты обновления данных
                self._data = parse_table(file, self._config.groups, self._config.second_shift, self._config.days, self._config.short, self._config.full, self._config.second_shift_delay) # Получение данных
                self.log(f"Глобальное расписание успешно загружено из файла \"{file}\".")
                return f"Глобальное расписание успешно загружено из файла \"{file}\".", False
            except Exception as ex: # В случае ошибки
                self.log.error(f"Произошла ошибка при попытке обработки файла \"{file}\". Продолжается работа на старых данных! Ошибка: {ex}")
                return f"Произошла ошибка при попытке обработки файла \"{file}\". Продолжается работа на старых данных! Ошибка: {ex}", True
        else: # Если файл не указан
            try:
                files = get_filenames(self._config.directory) # Получение имен файлов из папки
            except Exception as ex: # При ошибке обнаружения файлов
                self.log.error(f"Произошла ошибка при попытке обнаружения файлов директории \"{self._config.directory}\". Ошибка: {ex}")
                self.log.warning(f"Файл расписания не найден! Продолжается работа на старых данных!")
                return f"Произошла ошибка при попытке обнаружения файлов директории \"{self._config.directory}\". Ошибка: {ex} [WARNING] Файл расписания не найден! Продолжается работа на старых данных!", True
            else: # Если ошибка не возникла
                if len(files) == 0: # Если в списке нет ни одного файла
                    self.log.warning(f"Файл расписания не найден! Продолжается работа на старых данных!")
                    return f"В папке не обнаружены файлы с расписанием! Файл расписания не найден! Продолжается работа на старых данных!", True
                else:
                    try: # Попытка получения данных
                        self._updated = datetime.now()# Обновление даты обновления данных
                        self._data = parse_table(self._config.directory+files[0], self._config.groups, self._config.second_shift, self._config.days, 
                                                 self._config.short, self._config.full, self._config.second_shift_delay) # Получение данных
                        self.log(f"Глобальное расписание успешно загружено из файла \"{self._config.directory+files[0]}\".")
                        return f"Глобальное расписание успешно загружено из файла \"{self._config.directory+files[0]}\".", False
                    except Exception as ex: # В случае ошибки
                        self.log.error(f"Произошла ошибка при попытке обработки файла расписания из файла \"{self._config.directory+files[0]}\". Продолжается работа на старых данных! Ошибка: {ex}")
                        return f"Произошла ошибка при попытке обработки файла расписания из файла \"{self._config.directory+files[0]}\". Продолжается работа на старых данных! Ошибка: {ex}", True

    @property
    def data(self) -> dict:
        if not self._config.lifetime > 0:
            return self._data
        if datetime.now().timestamp() - self._updated.timestamp() > self._config.lifetime:
            self.log(f"Обновление расписания...")
            self._load_data()
        return self._data

    @property
    def default_data(self):
        return parse_table(self._config.schema_file, self._config.groups, self._config.second_shift, self._config.days, 
                           self._config.short, self._config.full, self._config.second_shift_delay)
    
    @property
    def teachers(self):
        return list(self._data['teachers'].keys())
    
    def update_data(self):
        return self._load_data()
    
    def prepare_iframe_data(self, days_to_do: int, columns: int = 5, skip: int = 0):
        months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
        weekdays = ['Понедельник', 'Вторник', 'Среду', 'Четверг', 'Пятницу', 'Субботу', 'Воскресенье']
        today = datetime.now()
        done = 0
        res = []
        days = []
        while done < days_to_do:
            today = datetime.now()+timedelta(days=skip+done)
            weekday = datetime.weekday(today)
            while ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][weekday] not in self._config.days:
                skip += 1
                today = datetime.now()+timedelta(days=skip+done)
                weekday = datetime.weekday(today)

            today = f'{weekdays[weekday]} {today.day} {months[today.month-1]}'
            
            days.append(self._config.days[weekday])
            res.append({
                    'day': today,
                    'data': [[]]
            })
            done += 1
        for i, day in enumerate(days):
            # i - номер расписания  day - порядковый номер дня недели
            for paralel in self.data['klasses']:
                # Перебор классов по возрастанию (5а, 5б ... 11б)
                if paralel in self._config.show:
                    for klass in self.data['klasses'][paralel]:
                        # Если класс есть в списке для показа (аргумент show в конфигурации)
                        if len(res[i]['data'][-1]) >= columns:
                            # Если в текущей строке >= таблицы, добавляем следующую строку
                            res[i]['data'].append([])
                        res[i]['data'][-1].append({
                            'klassname': klass.upper(),
                            'lessons': self._data['lessons'][klass][day]
                        })
        return res

    def save_data(self, day, data, file: str|None = None):
        if file: # Если файл шаблона указан
            try: # Попытка сохранения
                save_data_to_table(file, day, data)
                self.log(f"Данные успешно сохранены в \"{file}\".")
                return f"Данные успешно сохранены в \"{file}\"."
            except Exception as ex: # В случае ошибки
                self.log.error(f"Ошибка при сохранении данных в \"{file}\". Ошибка:\n{ex}")
                return f"Ошибка при сохранении данных в \"{file}\". Ошибка:\n{ex}"
        else: # Если файл не указан
            try:
                files = get_filenames(self._config.directory) # Получение имен файлов из папки
            except Exception as ex: # При ошибке обнаружения файлов
                self.log.error(f"Произошла ошибка при попытке обнаружения файлов директории \"{self._config.directory}\". Ошибка:\n{ex}")
                self.log.warning(f"Файл глобального расписания не найден! Продолжается работа на старых данных!")
                return f"Произошла ошибка при попытке обнаружения файлов директории \"{self._config.directory}\". Ошибка:\n{ex} \n\n[WARNING] Файл глобального расписания не найден! Продолжается работа на старых данных!"
            else: # Если ошибка не возникла
                if len(files) == 0: # Если в списке нет ни одного файла
                    self.log.warning(f"Файл глобального расписания не найден! Продолжается работа на старых данных!")
                    return f"В папке не обнаружены файлы с расписанием!\nФайл глобального расписания не найден! Продолжается работа на старых данных!"
                else:
                    try: # Попытка получения данных
                        self._glob_updated = datetime.now() # Обновление даты обновления данных
                        save_data_to_table(self._config.directory+files[0], day, data)
                        self.log(f"Данные успешно сохранены в \"{self._config.directory+files[0]}\".")
                        return f"Данные успешно сохранены в \"{file}\"."
                    except Exception as ex: # В случае ошибки
                        self.log.error(f"Ошибка сохранения данных в \"{self._config.directory+files[0]}\". Ошибка:\n{ex}")
                        return f"Ошибка сохранения данных в \"{self._config.directory+files[0]}\". Ошибка:\n{ex}"
        

def get_filenames(dir_path: str):
    # Получить имена файлов из папки остортированные от новых, к старым
    return sort_filenames([f for f in listdir(dir_path) if isfile(join(dir_path, f))])

def sort_filenames(files: list) -> list:
    # Отсортировать файлы, возвращает список имен файлов (оригинальных) отсортированных от нового к старому
    # Файлы должны быть названы в одинаковом формате
    # Пример: 15.11.23.xlsx, 16.11.23.xlsx
    # Или: 15_11_23.xlsx, 16_11_23.xlsx
    # Или: 15-11-23.xlsx, 16-11-23.xlsx
    dub = {}
    for i in range(len(files)):
        if not re.fullmatch(r'\d\d[-_.]\d\d[-_.]\d{4}\.(xls)?(xlsx)?(ods)?', files[i]):
            continue
        dub[files[i][:files[i].rfind('.')].replace('.', '-').replace('_', '-')] = files[i]

    res = []
    for k in sorted(dub.keys(), reverse=True, key=lambda x: datetime.strptime(x, '%d-%m-%Y')):
        res.append(dub[k])
    return res

class Carousel:
    """
    Класс для обработки карусели.
    При вызове возвращает путь до следующего файла.
    """
    video_extensions = ['mp4', 'webm', 'ogv', 'ogg']
    image_extensions = ['png', 'jpeg', 'jpg', 'webp', 'gif']
    allowed_extensions = video_extensions+image_extensions

    def __init__(self, directory: str = 'data/carousel/', skip_check: bool = False):
        self.directory = directory
        self.dir_abs_path = path.abspath(self.directory+'/')
        self.files = [f for f in listdir(directory) if isfile(join(directory, f)) and f[f.rfind('.')+1:] in self.allowed_extensions]
        if not skip_check and len(self.files) == 0:
            raise FileNotFoundError(f'Не найдены файлы для карусели в директории "{directory}"')
        self.sort()
        self._ind = 0

    def __call__(self, step: int = 1, index: int = None, absolute_path: bool = False) -> str:
        """Возвращает путь до следующего файла или, если указан step, возвращает путь до step файла
        :step: шаг (может быть отрицательным)
        :index: с какого индекса начинать (индекс должен быть легитимным)
        :absolute_path: True - для возврата абсолютного пути до файла, False - для возврата только имени файла
        """
        if index is None:
            ind = self._ind
        else:
            ind = index
        if step > 0 and ind+step >= len(self.files):
            ind = 0
        elif step < 0 and ind+step < 0:
            ind = len(self.files)+step-ind
        else:
            ind += step
        if index is None:
            self._ind = ind
        if absolute_path:
            return path.abspath(self.directory+self.files[ind])
        else:
            return self.files[ind]
    
    def next(self, cur: str = None) -> str:
        """Возвращает путь до следующего файла"""
        if cur is None:
            return self[0]
        return self.__call__(1, self.index(cur))
    
    def prev(self, cur: str = None) -> str:
        """Возвращает путь до предыдущего файла"""
        return self.previous(cur)
    
    def previous(self, cur: str = None) -> str:
        """Возвращает путь до предыдущего файла"""
        if cur is None:
            return self[0]
        return self.__call__(-1, self.index(cur))
    
    def set_null(self):
        """Устанавливает глобальный индекс в 0"""
        self._ind = 0

    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, key):
        return self.files[key]
    
    def __delitem__(self, key):
        del self.files[key]

    def __repr__(self) -> str:
        return '; '.join(self.files)
    
    def append(self, path: str):
        """Добавляет элемент"""
        if path not in self.files:
            self.files.append(path)
        else:
            raise FileExistsError(f'Файл с именем "{path}" уже существует.')

    def remove(self, item: str):
        """Удаляет элемент (не индекс, а сам элемент)"""
        self.__delitem__(self.index(item))

    def index(self, item: str):
        try:
            ind = self.files.index(item)
        except ValueError:
            raise ValueError(f'Неверный аргумент карусели! В списке нет элемента "{item}"')
        return ind

    def sort(self):
        """Сортирует список"""
        self.files.sort() 
