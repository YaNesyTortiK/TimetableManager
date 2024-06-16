import openpyxl
from src.tools.parser_ods import Parser
from openpyxl.styles import Alignment, Font
import re

class Settings:
    alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' # Алфавит для перебора столбцов
    def __init__(self, workbook: openpyxl.Workbook | Parser) -> None:
        self._workbook, self._sheet = workbook, workbook.active
        if self._sheet is None:
            self._sheet = workbook.worksheets[0]

    @property
    def settings(self):
        # Аргумент settings
        return self._get_settings()
    
    def _dig_down(self, dct: dict, k: int) -> dict|bool:
        if k == None:
            return False
        if k in dct.keys():
            k_val = dct[k]
            new_k = k-1
            del dct[k]
            self._dig_down(dct, new_k)
            dct[new_k] = k_val
            return dct
        else:
            return False
    
    def _get_settings(self):
        # Получение параметров таблицы
        val = 0
        pos = 'C' # С какого столбца начинаются расписания для классов
        klasses = {} # Столбцы для классов
        while val != None: # Пока имя класса не пустое
            val = self._sheet[f'{pos}1'].value # type: ignore Получение имени класса
            if val != None: # Если имя не пустое
                klasses[val] = pos # Сохраняем столбец для класса
                pos = self._next_pos(pos) # Берем следующую позицию

        days = {}
        val = 0
        pos = 2
        last_day = self._sheet[f'A2'].value # type: ignore
        day_lessons = {} # Временный словарь данных
        while val != None: # Пока значение не пустое
            val = self._sheet[f'B{pos}'].value # type: ignore Получаем номер урока
            day = self._sheet[f'A{pos}'].value # type: ignore Получаем значение ячейки дня недели
            if day != None: # Если ячейка с днем недели не пустая
                days[last_day] = day_lessons
                day_lessons = {} # Очищаем временный словарь
                last_day = day
            if val == None: # Если ячейка с номером урока пустая
                days[last_day] = day_lessons
                day_lessons = {} # Очищаем временный словарь
                break # Выхрдим из цикла
            day_lessons[int(val)] = pos
            pos += 1

        return (klasses, days)

    def _next_pos(self, cur_pos):
        # Функция получения имени следующего столбца
        # Прим: _next_pos('Z') -> 'AA'
        new_pos = ''
        add = True
        for x in cur_pos[::-1]:
            ind = self.alph.find(x)
            if add and ind+1 < len(self.alph):
                new_pos += self.alph[ind+1]
                add = False
            elif add and ind+1 >= len(self.alph):
                new_pos += self.alph[0]
            else:
                new_pos += x
        if add:
            new_pos += self.alph[0]
        return new_pos[::-1]
    
class ParserABC():
    def __init__(self, filepath: str, groups: dict[str, list], allowed_days: list, second_shift: list = [], 
                 second_shift_delay: int = 6, short_names: dict = {}, full_names: dict = {}) -> None:
        """
        Инициализация парсера.
        :filepath: type:str Путь до файла с расписанием. Пример: "/mnt/rasp/table.xlsx"
        :groups: Вручную заданные разделения по группам/параллелям. Пример: {"5": ["5а", "5б"], "Внеурочка": ['ГР1', 'ГР2']}
        :allowed_days: Дни недели для отображения (не внесенные дни, не будут обработаны). Обратите внимание, что строки в списке должны совпадать с сокращениями дня недели в таблице. Пример: ['Пн', 'Вт', ...]
        :second_shift: Список крупп/параллелей для отображения на второй смене. Пример: ["6", "Внеурочка"]. По умолчанию пусто.
        :second_shift_delay: Сдвиг смены. Если в таблице классы/группы выведенные на вторую смену смещены первым уроком на седьмой урок первой смены, то укажите значение "6". По умолчанию 6.
        :short_names: Сокращения для названий уроков (если не внесено, то будет отображаться как в таблице). Пример: {"Матем": "Мат", "Геометрия": "Геом"}. Используется для отображения в режиме показа нескольких классов и для вывода в iframe. По умолчанию пусто.
        :full_names: Развернутые названия уроков (если не внесено, то будет отображаться как в таблице). Пример: {"Матем": "Математика"}. Используется для отображения при отображении только одного класса (прим: при нажатии на класс и выводе всплывающего окна). По умолчанию пусто.
        """
        self.file = filepath
        self.groups = groups
        self.allowed_days = allowed_days
        self.second_shift = second_shift
        self.second_shift_delay = second_shift_delay
        self.short_names = short_names
        self.full_names = full_names

        self._data = self.parse()
    
    def parse(self) -> dict|NotImplementedError:
        """
        Функция парсинга. Возвращает данные в следующем виде:
        {
            'weekdays': ['Пн', 'Вт', ...],
            'klasses': {
                # group: group_list
                '5': ['5а', ...]
            },
            'lessons': {
                '5а': {
                    'Пн': [
                        {'val': [ # Разделено по \n
                                "Матем Антонов А.А. 208", 
                                "Русск Максимов Б.Б. 309"
                                ], 
                            # Если урок есть в full_names, то оно замениться
                            # пример: Матем -> Математика
                        'short': [ # Разделено по \n (Без учителя с сокращениями)
                            "Матем 208", 
                            "Русск 309"
                            ], # Если урок есть в short_names, то оно заменится на соответсвующее значение
                        'num': 0,
                        'true_num': 6, # Если параллель на второй смене, то её номер будет уменьшен для удобного просмотра но в программе нужно точное показание
                        'color': "#000000",
                        'data': [ Данные для представления на сервере конфигурации (оригинальные)
                                {
                                    'lesson': 'Матем',
                                    'teacher': 'Антонов А.А.',
                                    'kab': '208',
                                },
                                {
                                    'lesson': 'Русск',
                                    'teacher': 'Максимов Б.Б.',
                                    'kab': '309',
                                },
                            ]
                        },
                        ...
                    ],
                    ...
                },
                ...
            },
            'teachers': {
                'Антонов А.А.': {
                    'Пн': [
                        {
                            'val': "Матем Антонов А.А. 208\nРусск Максимов Б.Б. 309",
                                Если урок есть в full_names, то оно замениться
                                пример: Матем -> Математика
                            'num': 0,
                            'color': "#FF0000", # Красный цвет
                            'klassname': '5а',
                            'kab': '208',
                            'short': "Матем 208\nРусск 309"
                                Если урок есть в short_names, то оно заменится на соответсвующее значение
                        },
                        ...
                    ],
                    ...
                },
                ...
            },
            'settings': {
                'klasses': {
                    '5': ['5а', '5б'],
                    ...
                },
                'days': {
                    'Пн': {
                        1: 2 # Номер урока: строка в таблице
                        ...
                    }
                }
            }
        }
        """
        raise NotImplementedError('Данный класс является шаблоном или наследовавший класс не переопределил данную функцию.')
    
    @property
    def data(self) -> dict:
        """
        Returns data parsed from file.
        """
        return self._data

    @property
    def workbook(self):
        if self.file[self.file.rfind('.')+1:] in ['xls', 'xlsx']:
            return openpyxl.load_workbook(self.file) # Открываем файл таблицы
        elif self.file[self.file.rfind('.')+1:] == 'ods':
            return Parser(self.file)

    def reparse(self) -> None:
        self._data = self.parse()
    
    def prepare_data(self) -> dict:
        """
        Генерирует чистый словарь с данными:
        {
            '5а': {
                'Пн': {
                    1: ['Матем Иванов А.А. 123', "#000000"] # Строка и цвет
                    ...
                }
            }
            '6а': { # Вторая смена
                'Пн': {
                    1: [None, "#000000"] # None - нет значения
                    ...
                    6: ['Матем Иванов А.А. 123', "#000000"] # Строка и цвет
                }
            }
        }
        """
        res = {}
        wb = self.workbook
        sheet = wb.active # Получаем активный лист
        if sheet is None: # Если нет активного листа
            sheet = wb.worksheets[0] # Принимаем первый лист за активный
        klasses, days = Settings(wb).settings # Получаем параметры таблицы
        for klass, col in klasses.items():
            res[klass] = {}
            for day, pointers in days.items():
                res[klass][day] = {}
                for lesson, row in pointers.items():
                    color = get_color(wb, f'{col}{row}')
                    val = sheet[f'{col}{row}'].value
                    res[klass][day][lesson] = [val, color]
        return res

class ClassicParser(ParserABC):
    def __init__(self, filepath: str, groups: dict[str, list], allowed_days: list, second_shift: list = [], second_shift_delay: int = 6, short_names: dict = {}, full_names: dict = {}) -> None:
        super().__init__(filepath, groups, allowed_days, second_shift, second_shift_delay, short_names, full_names)

    def parse(self) -> dict:
        groups = self.groups
        allowed_days = self.allowed_days
        second_shift = self.second_shift
        second_shift_delay = self.second_shift_delay
        short_names = self.short_names
        full_names = self.full_names
        wb = self.workbook
        sheet = wb.active # Получаем активный лист
        if sheet is None: # Если нет активного листа
            sheet = wb.worksheets[0] # Принимаем первый лист за активный
        klasses, days = Settings(wb).settings # Получаем параметры таблицы

        if short_names == None:
            short_names = {}
        if full_names == None:
            full_names = {}

        teachers = {}
        parallels = {}
        for klass in klasses.keys(): # Распределение классов по параллелям
            for group, ingroup in groups.items():
                if klass in ingroup:
                    if group not in parallels.keys():
                        parallels[group] = []
                    if klass not in parallels[group]:
                        parallels[group].append(klass)
                    break
            else:
                # Если класс не определен в группу
                if klass[:-1] not in parallels.keys():
                    parallels[klass[:-1]] = []
                parallels[klass[:-1]].append(klass)
        
        for par in parallels.keys():
            parallels[par] = sorted(parallels[par])

        better_second_shift = []
        for group in second_shift:
            if group in parallels.keys():
                for item in parallels[group]:
                    better_second_shift.append(item)
        second_shift = better_second_shift
        
        timetable = {}
        for klass in klasses.keys():
            table = {}
            for day in days.keys():
                if day not in allowed_days:
                    continue
                if day in table.keys():
                    raise Warning("В файле найдены повторяющиеся дни!")
                table[day] = []
                added = False
                for num in days[day].keys():
                    color = get_color(wb, f'{klasses[klass]}{days[day][num]}')
                    val = sheet[f'{klasses[klass]}{days[day][num]}'].value # type: ignore
                    if klass in second_shift:
                        num = num-second_shift_delay
                    if val == None or val == ' ' or val == '' or val.strip() == '':
                        if klass in second_shift:
                            if not added:
                                continue
                        else:
                            if added:
                                continue
                    else:
                        added = True
                    parsed = self._parse_teachers(val)
                    # Убираем повторяющиеся уроки для одного класса
                    # Было:  Ифнорматика 321 Информатика 123
                    # Стало: Информатика 321 123
                    if parsed:
                        short_val = []
                        l_lesson = None
                        for p in parsed:
                            _lsn = p[0]
                            if l_lesson == None:
                                l_lesson = p[0]
                            elif l_lesson == p[0]:
                                _lsn = ''
                            short_val.append((_lsn, p[1], p[2]))
                    # ------
                    table[day].append(  
                        {
                            'num': num,
                            'true_num': num+second_shift_delay if klass in second_shift else num,
                            'val': [
                                f"{full_names[p[0]] if p[0] in full_names.keys() else p[0]} {p[1]} {p[2]}" for p in parsed 
                            ] if parsed != None else [None],
                            'color': color,
                            'short': [
                                f"{short_names[p[0]] if p[0] in short_names.keys() else p[0]} {p[2]}" for p in short_val
                            ] if parsed != None else [None],
                            'data': [
                                {
                                    'lesson': p[0],
                                    'teacher': p[1],
                                    'kab': p[2]
                                } for p in parsed
                            ] if parsed != None else [{'lesson': None, 'teacher': None, 'kab': None}]

                        }
                    )
                    if parsed:
                        for lsn in parsed:
                            if lsn[1] not in teachers.keys():
                                teachers[lsn[1]] = {}
                            if day not in teachers[lsn[1]].keys():
                                teachers[lsn[1]][day] = []
                            teachers[lsn[1]][day].append(
                                {
                                    'num': num+second_shift_delay if klass in second_shift else num,
                                    'val': [
                                            f"{full_names[p[0]] if p[0] in full_names.keys() else p[0]} {p[1]} {p[2]}" for p in parsed
                                        ] if parsed != None else [None],
                                    'color': color,
                                    'klassname': klass,
                                    'kab': lsn[2],
                                    'short': [
                                        f"{short_names[p[0]] if p[0] in short_names.keys() else p[0]} {p[2]}" for p in short_val
                                    ] if parsed != None else [None]
                                }
                            )
                if not added: # Если в расписании ничего нет, очищаем список
                    table[day] = []
            timetable[klass] = table
        
        new_pars = {}
        for k in self._sort_klasses(parallels.keys()):
            new_pars[k] = parallels[k]
        parallels = new_pars

        wb.close() # Закрываем файл таблицы
        return self._sort_table(self._beautify_table({
            'weekdays': list(x for x in days.keys() if x in allowed_days),
            'klasses': parallels,
            'lessons': timetable,
            'teachers': teachers,
            'settings': {
                'klasses': parallels,
                'days': days
            }
        }, second_shift))

    def _parse_teachers(self, s: str):
        # Функция разделения данных в ячейке на подгруппы внутри класса и разделение на Урок/Учитель/Кабинет
        if s == None or s == '' or s == ' ':
            return None # Если строка пустая
        s = s.split('\n') # type: ignore Разделяем класс на подгруппы по переносу строки
        ns = [] # Список подгрупп
        for x in s: # Перебираем подгруппы
            x = x.strip() # очищаем строку от лишних пробелов справа и слева
            if x == '' or x == None or x == " " or x.strip() == '':
                continue # Если строка пустая, пропускаем подгруппу
            kab_indx = x.rfind(' ')+1 if x[-1].isdigit() or x[-1:] == '-' or x[-2:] == 'нч' else None # Находим место нахождения номера кабинета в строке
            if kab_indx == None: # Если номер кабинета не найден
                kab = x[x.rfind(' ')+1:] # Устанавливаем кабинет строкой от правого пробела, до конца строки
                kab_indx = None
            else:
                kab = x[kab_indx:]
            x = x[:kab_indx-1] if kab_indx != None else x # Убираем из строки кабинет
            teacher_indx = x[:x.rfind(' ')].rfind(' ') # Ищем индекс символа начала ФИО учителя
            # !!! ФИО в формате Иванов. И.И. (ПРОБЕЛ МЕЖДУ ФАМИЛИЕЙ И ИНИЦИАЛАМИ ОБЯЗАТЕЛЕН)
            teacher = x[teacher_indx+1:] # Получаем строку с ФИО учителя
            lesson = x[:teacher_indx] # Получаем строку названия урока
            ns.append([lesson, teacher, kab]) # Добавляем подгруппу
        return ns

    def _sort_table(self, table: dict) -> dict:
        # Функция сортировки и преобразования словаря для удобного представления данных
        for klass in table['lessons'].keys():
            for day in table['lessons'][klass].keys():
                table['lessons'][klass][day] = sorted(table['lessons'][klass][day], key=lambda x: x['num'])
        
        for teacher in table['teachers'].keys():
            for day in table['teachers'][teacher].keys():
                table['teachers'][teacher][day] = sorted(table['teachers'][teacher][day], key=lambda x: x['num'])

        tchrs = {}
        for teacher in sorted(table['teachers'].keys()):
            tchrs[teacher] = table['teachers'][teacher]
        table['teachers'] = tchrs
        
        return table

    def _beautify_table(self, table: dict, second_shift: list) -> dict:
        # Функция приведения всех таблиц классов к общему формату
        # Если для класса из параллели имеется 7 урок, а устальных нет, для всех остальных добавится пустой урок 
        for paralel in table['klasses'].keys():
            day_lessons = {}
            # Находим для каждой параллели минимальный и максимальный по счету урок
            for klass in table['klasses'][paralel]:
                for day in table['lessons'][klass].keys():
                    if day not in day_lessons.keys() or day_lessons[day] == None:
                        if paralel in second_shift:
                            day_lessons[day] = 1
                        else:
                            day_lessons[day] = 1
                    nums = [x['num'] for x in table['lessons'][klass][day]]
                    if len(nums) == 0:
                        day_lessons[day] = None
                        continue
                    if klass in second_shift:
                        mn = min(nums)
                        if mn < day_lessons[day]:
                            day_lessons[day] = mn
                    else:
                        mn = max(nums)
                        if mn > day_lessons[day]:
                            day_lessons[day] = mn
            # Добавляем к каждому классу недостающее количество уроки до одинакового количества строк таблицы для параллели
            for klass in table['klasses'][paralel]:
                for day in table['lessons'][klass].keys():
                    nums = [x['num'] for x in table['lessons'][klass][day]]
                    if day_lessons[day] == None or len(nums) == 0:
                        continue
                    # Добавляем пустые строки если есть окна
                    for i in range(min(nums), max(nums)+1):
                        if i not in nums:
                            table['lessons'][klass][day].append(
                                    {
                                        'num': i,
                                        'val': None,
                                        'color': '000000',
                                        'short': None
                                    }
                                )
                    if klass in second_shift:
                        # Добавляем строки до первого урока
                        mn = min(nums)
                        if day_lessons[day] < mn:
                            for i in range(day_lessons[day], mn):
                                table['lessons'][klass][day].append(
                                    {
                                        'num': i,
                                        'val': None,
                                        'color': '000000',
                                        'short': None
                                    }
                                )
                    else:
                        # Добавляем строки после последнего урока
                        mn = max(nums)
                        if day_lessons[day] > mn:
                            for i in range(mn+1, day_lessons[day]+1):
                                table['lessons'][klass][day].append(
                                    {
                                        'num': i,
                                        'val': None,
                                        'color': "#000000",
                                        'short': None
                                    }
                                )
        return table

    def _sort_klasses(self, klasses: list[str]) -> list:
        """
        Sorts klasses (All items MUST be str type). FirstL numbers low -> big, then words alphabetically
        Example:
        in: ['1', '10', '2', 'cba', 'abc']
        out: ['1', '2', '10', 'abc', 'cba']
        """
        nums = sorted([x for x in klasses if x.isdigit()], key=lambda x: int(x) if type(x) != int else x)
        words = sorted([x for x in klasses if not x.isdigit()])
        return nums+words
    
class AdaptiveParser(ParserABC):
    def __init__(self, filepath: str, groups: dict[str, list], allowed_days: list, second_shift: list = [], second_shift_delay: int = 6, short_names: dict = {}, full_names: dict = {}) -> None:
        super().__init__(filepath, groups, allowed_days, second_shift, second_shift_delay, short_names, full_names)
    
    def parse(self) -> dict:
        wb = self.workbook
        sheet = wb.active # Получаем активный лист
        if sheet is None: # Если нет активного листа
            sheet = wb.worksheets[0] # Принимаем первый лист за активный
        klasses, days = Settings(wb).settings # Получаем параметры таблицы
        
        parallels = {}
        for klass in klasses.keys(): # Распределение классов по параллелям
            for group, ingroup in self.groups.items():
                if klass in ingroup:
                    if group not in parallels.keys():
                        parallels[group] = []
                    if klass not in parallels[group]:
                        parallels[group].append(klass)
                    break
            else:
                # Если класс не определен в группу
                if klass[:-1] not in parallels.keys():
                    parallels[klass[:-1]] = []
                parallels[klass[:-1]].append(klass)
        
        for par in parallels.keys():
            parallels[par] = sorted(parallels[par])

        better_second_shift = []
        for group in self.second_shift:
            if group in parallels.keys():
                for item in parallels[group]:
                    better_second_shift.append(item)

        clean_data = self.prepare_data()
        lessons = {}
        teachers = {}
        
        for klass, days in clean_data.items():
            lessons[klass] = {}
            for day, data in days.items():
                if day not in self.allowed_days:
                    continue # Если день не входит в allowed_days - пропускаем
                lessons[klass][day] = []
                for num, value in data.items(): # где value=[строка из таблицы, цвет]
                    if value[0] is None: # Если нет даннных - пропускаем
                        continue
                    cur = {
                        'val': [],
                        'short': [],
                        'true_num': int(num),
                        'num': int(num-self.second_shift_delay) if klass in better_second_shift else int(num),
                        'color': value[1],
                        'data': []
                    }
                    included_teachers = [] # [{'teacher': '', 'klass': '', kab: ''}]
                    for part in value[0].split('\n'):
                        parsed = self._parse_value(part)
                        cur['val'].append(
                            str(self.full_names[parsed['lesson']] if parsed['lesson'] in self.full_names.keys() else parsed['lesson']) + ' ' + \
                            str(parsed['teacher']) + ' ' + \
                            str(parsed['kab'])
                        )
                        similar = False
                        if len(cur['data']) > 0: # Проверка на совпадение
                            if cur['data'][-1]['lesson'] == parsed['lesson']: # Если урок совпадает с предыдущим
                                cur['short'][-1] += ' '+parsed['kab']
                                similar = True
                        if not similar:
                            cur['short'].append(
                                str(self.short_names[parsed['lesson']] if parsed['lesson'] in self.short_names.keys() else parsed['lesson']) + ' ' +\
                                str(parsed['kab'])
                            )
                        cur['data'].append(parsed)
                        if parsed['teacher'] != "":
                            included_teachers.append({
                                'teacher': parsed['teacher'],
                                'klass': klass,
                                'kab': parsed['kab']
                            })
                    # Генерация учительского расписания
                    for teacher_data in included_teachers:
                        if teacher_data['teacher'] not in teachers.keys():
                            teachers[teacher_data['teacher']] = {}
                        if day not in teachers[teacher_data['teacher']].keys():
                            teachers[teacher_data['teacher']][day] = []
                        teachers[teacher_data['teacher']][day].append({
                            'val': cur['val'],
                            'short': cur['short'],
                            'color': value[1],
                            'num': num,
                            'klassname': teacher_data['klass'],
                            'kab': teacher_data['kab']
                        })
                            
                    lessons[klass][day].append(cur)

        return {
            "weekdays": [i for i in self.allowed_days if i in days.keys()],
            "klasses": parallels,
            "lessons": self._beautify_table(lessons, parallels, better_second_shift),
            "teachers": self._sort_teacher_table(teachers),
            "settings": {
                "klasses": parallels,
                "days": days
            }
        }

    def _parse_value(self, value: str):
        teacher_mask = re.compile(r"([ .,]|^)[А-ЯA-Z]{1}[а-яa-z]{0,}[ .,][А-ЯA-Z]{1}[ .,][А-ЯA-Z]{1}([ .,]|$)") # Выражения для поиска учителя в строке (см. в примерах ниже)
        """
        Парсинг отдельной строки с данными. Примеры входа-выхода:
        Обратите внимание, что для правильной 'обработки' учителя, первый символ фамилии и инициалов должен быть большой буквой. (Учителей надо уважать)
        1: 
            In: "Матем Иванов А.А. 123"
            Out: {
                "lesson": "Матем",
                "teacher": "Иванов А.А.",
                "kab": "123"
            }
        2: 
            In: "Матем 123"
            Out: {
                "lesson": "Матем",
                "teacher": "",
                "kab": "123"
            }
        3: 
            In: "Матем"
            Out: {
                "lesson": "Матем",
                "teacher": "",
                "kab": ""
            }
        4: 
            In: "Русский язык" # В данном случае 'язык' не будет являться кабинетом, так как не содержит цифр
            Out: {
                "lesson": "Русский язык",
                "teacher": "",
                "kab": ""
            }
        5:
            In: "Русский язык111" # В данном случае 'язык111' будет являться кабинетом, так как содержит цифры
            Out: {
                "lesson": "Русский",
                "teacher": "",
                "kab": "язык111"
            }
        6: 
            In: "Русский Иванов А.А." # В данном случае Иванов А.А. совпадает с регулярным выражением:
                r"([ .,]|^)[А-ЯA-Z]{1}[а-яa-z]{0,}[ .,][А-ЯA-Z]{1}[ .,][А-ЯA-Z]{1}([ .,]|$)"
                Другие совпадения: Иванов А.А ; Иванов.А.А. ; Иванов.А.А ; 
            Out: {
                "lesson": "Русский",
                "teacher": "Иванов А.А.",
                "kab": ""
            }
        7: 
            In: "Музыка актовый зал" # В данном случае 'актовый зал' будет являться кабинетом, только в случае, если 'Музыка' будет являться ключом в short_names или full_names
            Out: {
                "lesson": "Музыка",
                "teacher": "",
                "kab": "актовый зал"
            }
        8: 
            In: "Музыка актовый зал" # В данном случае 'Музыка' не является ключом в short_names или full_names, следовательно вся строка будет считаться уроком
            Out: { 
                "lesson": "Музыка актовый зал",
                "teacher": "",
                "kab": ""
            }
        9: 
            In: "Музыка Иванова А.А. актовый зал" # В данном случае 'музыка' не обязательно должна находится в ключах short_names или full_names, так как учитель считается разделителем между уроком и кабинетом
            Out: { 
                "lesson": "Музыка",
                "teacher": "Иванова А.А.",
                "kab": "актовый зал"
            }
        """
        res = {
            "lesson": "",
            "teacher": "",
            "kab": ""
        }
        value = value.strip() # Очищаем строку от начальных и конечных пробелов и ненужных переносов строк
        if len(value.split(' ')) == 1: # Если в строке только одно слово (разделение пробелом)
            res['lesson'] = value # Вся строка будет являться уроком
            return res # Возвращаем результат с пустыми 'teacher' и 'kab'
        if any([x.isnumeric() for x in value.split(' ')[-1]]): # Если последнее слово (разделение пробелом) в строке содержит цифры
            res['kab'] = value.split(' ')[-1] # Записываем последнее слово как кабинет
            value = value[:value.rfind(' ')] # Убираем из строки последнее слово(кабинет) (чтобы не мешало, не ну а че оно)
        if re.search(teacher_mask, value) is None: # Если regex не нашел совпадение по 'маске учителя' (не указан учитель)
            if res['kab'] == "": # Если уабинет еще не выявлен
                # Проверяем наличие одного из уроков описанных в short_names или full_names для выделения возможного кабинета
                for possible_lesson in set(list(self.short_names.keys())+list(self.full_names.keys())):
                    if possible_lesson.lower()+' ' in value.lower(): # Если найдена подстрока (добавлен пробел, чтобы обработать окончания) (переведено в нижний регистр, чтобы исправить возможные опечатки по регистру)
                        temp_val = value.lower().replace(possible_lesson.lower(), '~') # Создаем временную строку с вырезанным возможным уроком
                        if temp_val[0] == '~': # Проверяем, что строка начиналась с данного урока, чтобы избежать ложного совпадения (к примеру possible_lesson="музыка" является подстрокой temp_val="классическая музыка прошлого века", однако если отбросить "прошлого века" в кабинет, может случится недопонимание)
                            res['kab'] = temp_val[1:].strip() # Записываем кабинет в результат
                            value = value[:value.find(res['kab'])].strip() # Убираем кабинет из строки
                            break # Выходим из цикла, так как уже найдено
            res['lesson'] = value.strip() # Записываем всю строку (оставшуюся, если был вырезан кабинет) как урок
            return res # Возвращаем результат с пустым полем "teacher"
        if re.fullmatch(teacher_mask, value.strip()): # Если строка полностью удовлетворяет 'маске учителя' (Нет других символов)
            res['lesson'] = value.strip() # Считаем, что такая ситуация некорректна и записываем всю строку как урок
            return res # Возвращаем результат с пустым полем "teacher"
        # Если до этого не был возвращен результат
        res['teacher'] = re.search(teacher_mask, value).group().strip()
        res['lesson'] = value[:re.search(teacher_mask, value).start()].strip()
        temp = value[re.search(teacher_mask, value).end():].strip()
        res['kab'] = temp+(' ' if temp != "" else "" + res['kab'] if res['kab'] != "" else "") # Считаем строку после учителя кабинетом (даже если она уже была задана) (Добавляем старое значение через пробел, так как могло обрезать ранее)
        return res

    def _beautify_table(self, data: dict, parallels: dict, better_second_shift: list) -> dict:
        """
        Добавляет пустые уроки, чтобы сравнять параллели по количеству уроков для более удобного просмотра.
        Принимает словарь lessons и parallels
        Возвращает словарь lessons
        """
        parallels_data = {} # Словарь из: {параллель: {день: [минимальный урок (true_num), максимальный урок (true_num)]}}
        for parallel in parallels:
            parallels_data[parallel] = {}
            for day in self.allowed_days:
                parallels_data[parallel][day] = [99, -99]
        
        # Находим минимальные и максимальные значения для каждой параллели
        for klass, days in data.items():
            klass_data = {}
            for day, values in days.items():
                mi, mx = 99, -99
                for val in values: # находим минимальный и максимальный урок для конкретного класса в онкретный день
                    if val['true_num'] < mi:
                        mi = val['true_num']
                    if val['true_num'] > mx:
                        mx = val['true_num']
                klass_data[day] = [mi, mx]
            # Находим нужную параллель
            for parallel, klasses in parallels.items():
                if klass in klasses:
                    for day, val in klass_data.items():
                        parallels_data[parallel][day] = [min(parallels_data[parallel][day][0], val[0]), max(parallels_data[parallel][day][1], val[1])]
                    break
        # Выравниваем количество
        for parallel, days in parallels_data.items():
            for day, ms in days.items():
                for klass in parallels[parallel]:
                    already_existing = [elem['true_num'] for elem in data[klass][day]]
                    new_data = []
                    for add_num in range(ms[0], ms[1]+1):
                        if add_num not in already_existing:
                            new_data.append({
                                'val': [None], 
                                'short': [None],
                                'num': add_num-self.second_shift_delay if klass in better_second_shift else add_num,
                                'true_num': add_num,
                                'color': "#000000",
                                'data': {"lesson": None, "teacher": None, "kab": None}
                            })
                        else:
                            new_data.append(data[klass][day][already_existing.index(add_num)])
                    data[klass][day] = new_data
        return data
    
    def _sort_teacher_table(self, data: dict):
        """
        Сортирует расписание учителей (по номеру урока)
        Принимает 'teachers' из data.
        Возвращает отсортированный список
        """
        res = {}
        for teacher, days in data.items():
            res[teacher] = {}
            for day, values in days.items():
                vals = sorted(values, key=lambda x: x['num'])
                res[teacher][day] = vals
        return res

class SimpleParser(ParserABC):
    """
    Парсер без распознавания уроков, учителей, кабинетов. Без изменений в соответствии с short_names и full_names. 
    """
    def __init__(self, filepath: str, groups: dict[str, list], allowed_days: list, second_shift: list = [], second_shift_delay: int = 6, short_names: dict = {}, full_names: dict = {}) -> None:
        super().__init__(filepath, groups, allowed_days, second_shift, second_shift_delay, short_names, full_names)
    
    def parse(self):
        wb = self.workbook
        sheet = wb.active # Получаем активный лист
        if sheet is None: # Если нет активного листа
            sheet = wb.worksheets[0] # Принимаем первый лист за активный
        klasses, days = Settings(wb).settings # Получаем параметры таблицы
        
        parallels = {}
        for klass in klasses.keys(): # Распределение классов по параллелям
            for group, ingroup in self.groups.items():
                if klass in ingroup:
                    if group not in parallels.keys():
                        parallels[group] = []
                    if klass not in parallels[group]:
                        parallels[group].append(klass)
                    break
            else:
                # Если класс не определен в группу
                if klass[:-1] not in parallels.keys():
                    parallels[klass[:-1]] = []
                parallels[klass[:-1]].append(klass)
        
        for par in parallels.keys():
            parallels[par] = sorted(parallels[par])

        better_second_shift = []
        for group in self.second_shift:
            if group in parallels.keys():
                for item in parallels[group]:
                    better_second_shift.append(item)

        clean_data = self.prepare_data()
        lessons = {}

        for klass, days in clean_data.items():
            lessons[klass] = {}
            for day, data in days.items():
                if day not in self.allowed_days:
                    continue # Если день не входит в allowed_days - пропускаем
                lessons[klass][day] = []
                for num, value in data.items(): # где value=[строка из таблицы, цвет]
                    if value[0] is None: # Если нет даннных - пропускаем
                        continue
                    cur = {
                        'val': [value[0]],
                        'short': [value[0]],
                        'true_num': int(num),
                        'num': int(num-self.second_shift_delay) if klass in better_second_shift else int(num),
                        'color': value[1],
                        'data': [{"lesson": value[0], "teacher": None, "kab": None}]
                    }
                    lessons[klass][day].append(cur)

        return {
            "weekdays": [i for i in self.allowed_days if i in days.keys()],
            "klasses": parallels,
            "lessons": self._beautify_table(lessons, parallels, better_second_shift),
            "teachers": {},
            "settings": {
                "klasses": parallels,
                "days": days
            }
        }
    
    def _beautify_table(self, data: dict, parallels: dict, better_second_shift: list) -> dict:
        """
        Добавляет пустые уроки, чтобы сравнять параллели по количеству уроков для более удобного просмотра.
        Принимает словарь lessons и parallels
        Возвращает словарь lessons
        """
        parallels_data = {} # Словарь из: {параллель: {день: [минимальный урок (true_num), максимальный урок (true_num)]}}
        for parallel in parallels:
            parallels_data[parallel] = {}
            for day in self.allowed_days:
                parallels_data[parallel][day] = [99, -99]
        
        # Находим минимальные и максимальные значения для каждой параллели
        for klass, days in data.items():
            klass_data = {}
            for day, values in days.items():
                mi, mx = 99, -99
                for val in values: # находим минимальный и максимальный урок для конкретного класса в онкретный день
                    if val['true_num'] < mi:
                        mi = val['true_num']
                    if val['true_num'] > mx:
                        mx = val['true_num']
                klass_data[day] = [mi, mx]
            # Находим нужную параллель
            for parallel, klasses in parallels.items():
                if klass in klasses:
                    for day, val in klass_data.items():
                        parallels_data[parallel][day] = [min(parallels_data[parallel][day][0], val[0]), max(parallels_data[parallel][day][1], val[1])]
                    break
        # Выравниваем количество
        for parallel, days in parallels_data.items():
            for day, ms in days.items():
                for klass in parallels[parallel]:
                    already_existing = [elem['true_num'] for elem in data[klass][day]]
                    new_data = []
                    for add_num in range(ms[0], ms[1]+1):
                        if add_num not in already_existing:
                            new_data.append({
                                'val': [None], 
                                'short': [None],
                                'num': add_num-self.second_shift_delay if klass in better_second_shift else add_num,
                                'true_num': add_num,
                                'color': "#000000",
                                'data': {"lesson": None, "teacher": None, "kab": None}
                            })
                        else:
                            new_data.append(data[klass][day][already_existing.index(add_num)])
                    data[klass][day] = new_data
        return data

def save_data_to_table(file: str, day: str, data: dict):
    wb = openpyxl.load_workbook(file) # Открываем файл таблицы
    sheet = wb.active # Получаем активный лист
    if sheet is None: # Если нет активного листа
        sheet = wb.worksheets[0] # Принимаем первый лист за активный
    klasses, days = Settings(wb).settings # Получаем параметры таблицы
    for klass in data.keys():
        for num in data[klass].keys():
            if len(data[klass][num]) == 1 and data[klass][num][0]['lesson'] is None:
                val = sheet[f'{klasses[klass]}{days[day][int(num)]}'].value  # type: ignore
                if val is None or val.strip() == '':
                    continue
                else:
                    sheet[f'{klasses[klass]}{days[day][int(num)]}'] = '' # type: ignore
                    continue
            s = '\n'.join([f'{p["lesson"].strip()} {p["teacher"].strip()} {p["kab"].strip()}'
                            for p in data[klass][num] if not p['lesson'] is None])
            sheet[f'{klasses[klass]}{days[day][int(num)]}'] = s # type: ignore
            sheet[f'{klasses[klass]}{days[day][int(num)]}'].alignment = Alignment(wrapText=True) # type: ignore
            sheet[f'{klasses[klass]}{days[day][int(num)]}'].font = Font(color=data[klass][num][0]['color'].replace("#", '').upper()) # type: ignore
    wb.save(file)
    wb.close()

def get_color(workbook: openpyxl.Workbook, pointer: str):
    try:
        active = workbook.active
        if active is None:
            active = workbook.worksheets[0]
        color = active[pointer].font.color.rgb # type: ignore
        if len(color) != 8:
            raise AttributeError
    except:
        return "#000000"
    else:
        return '#'+color[2:]
