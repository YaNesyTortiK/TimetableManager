import openpyxl
from src.tools.parser_ods import Parser
from openpyxl.styles import Alignment, Font

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

def _parse_teachers(s: str):
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

def _sort_table(table: dict) -> dict:
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

def _beautify_table(table: dict, second_shift: list) -> dict:
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

def _sort_klasses(klasses: list[str]) -> list:
    """
    Sorts klasses (All items MUST be str type). FirstL numbers low -> big, then words alphabetically
    Example:
    in: ['1', '10', '2', 'cba', 'abc']
    out: ['1', '2', '10', 'abc', 'cba']
    """
    nums = sorted([x for x in klasses if x.isdigit()], key=lambda x: int(x) if type(x) != int else x)
    words = sorted([x for x in klasses if not x.isdigit()])
    return nums+words


def parse_table(file: str, groups: dict[str, list], second_shift: list, allowed_days: list, short_names: dict, full_names: dict, second_shift_delay: int):
    """
    Returns:
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
                    'num': "0",
                    'true_num': "6", # Если параллель на второй смене, то её номер будет уменьшен для удобного просмотра но в программе нужно точное показание
                    'color': "FFFF0000",
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
                        'num': '0',
                        'color': "FFFF0000",
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
            'klasses': [],
            'days': []
        }
    }
    """
    if file[file.rfind('.')+1:] in ['xls', 'xlsx']:
        wb = openpyxl.load_workbook(file) # Открываем файл таблицы
    elif file[file.rfind('.')+1:] == 'ods':
        wb = Parser(file)
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
                parsed = _parse_teachers(val)
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
    for k in _sort_klasses(parallels.keys()):
        new_pars[k] = parallels[k]
    parallels = new_pars

    wb.close() # Закрываем файл таблицы
    return _sort_table(_beautify_table({
        'weekdays': list(x for x in days.keys() if x in allowed_days),
        'klasses': parallels,
        'lessons': timetable,
        'teachers': teachers,
        'settings': {
            'klasses': parallels,
            'days': days
        }
    }, second_shift))

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
            print(color)
            raise AttributeError
    except:
        return "#000000"
    else:
        return '#'+color[2:]
