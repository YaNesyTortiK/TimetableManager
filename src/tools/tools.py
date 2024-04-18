import jinja2

def render_jinja(template_loc: str, file_name: str, **context) -> str:
    """
    Функция используется для рендеринга шаблонов не требующих app context от Flask

    :template_loc: Директория где находится шаблон
    :file_name: Имя файла-шаблона
    :context: Переменные переменные передаваемые шаблонизатору

    -> rendered page
    """
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_loc+'/')
    ).get_template(file_name).render(context)