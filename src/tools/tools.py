import jinja2
import datetime

def render_jinja(template_loc: str, file_name: str, **context) -> str:
    """
    Функция используется для рендеринга шаблонов не требующих app context от Flask

    :template_loc: Директория где находится шаблон
    :file_name: Имя файла-шаблона
    :context: Переменные передаваемые шаблонизатору

    -> Отрендеренная страница
    """
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_loc+'/')
    ).get_template(file_name).render(context)

def pick_bells(bells: list[dict], weekdays: list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']) -> dict:
    """
    Функция для подбора подходящего расписания звонков на текущий день

    :bells: Список расписаний звонков из конфигурации
    :weekdays: Список сокращенных названий дней (должны совпадать с теми, которые используются в options в конфигурации расписания звонков)

    -> Актуальное расписание звонков
    """
    date = datetime.datetime.now().strftime('%Y-%m-%d') # Получаем текущую дату
    weekday = weekdays[datetime.datetime.weekday(datetime.datetime.now())] # Получаем текущий день недели (0-6) и преобразуем его в строковое значение из списка weekdays
    # Проход для поиска расписания на данную дату
    for table in bells:
        if table['type'] == 'date' and table['options'] == date:
            return _clean_bells(table)
    # Проход для поиска расписания на текущий день недели
    for table in bells:
        if table['type'] == 'weekday' and weekday in table['options']:
            return _clean_bells(table)
    # Проход для поиска расписания на все дни
    for table in bells:
        if table['type'] == 'all':
            return _clean_bells(table)
    # Если ничего не найдено, возвращается пустой словарь
    return {}

def _clean_bells(bells: dict) -> dict:
    """
    Убирает из словарей звонков type и options
    """
    res = {}
    for k,i in bells.items():
        if k not in ['type', 'options']:
            res[k] = i
    return res
