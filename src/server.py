from flask import Flask, render_template, redirect, request, abort, send_file
import flask_login
import os.path
import uuid
from datetime import datetime
import re
import subprocess
import json
import io

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

from src.tools.storage import Storage, get_filenames, Carousel
from src.tools.config_parser import Config
from src.tools.logger import Logger
from src.tools.tools import render_jinja, pick_bells

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

config = Config('config.json')

app = Flask(__name__) # Инициализация сервера
app.config['SECRET_KEY'] = uuid.uuid4().hex # Установка ключа для системы сессий

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# Storage & logger & carousel setup vvv
storage = Storage(config)
log = Logger(config.log_filename, config.log_to_console)
log('Запуск сервера')
try:
    carousel = Carousel(config.carousel_directory)
except FileNotFoundError:
    config.carousel = False
    log.warning('Не найдены данные для карусели. Карусель автоматически отключена.')
except Exception as ex:
    config.carousel = False
    log.error(f'Произошла непредвиденная ошибка при инциализации карусели: {ex}. Карусель автоматически отключена.')
finally:
    carousel = Carousel(config.carousel_directory, skip_check=True) # Создаем пустую карусель (для возможной загрузки файлов)
# End of storage & logger & carousel setup ^^^

# Data updater setup vvv
def periodic_task():
    storage.update_data()
    if config.save_iframe:
        r = save_iframe()
        if r[1] == 200:
            log.info(f'Асинхронное сохранение iframe: {r[0]}')
        else:
            log.warning(f'Асинхронное сохранение iframe: {r[0]}')

if config.lifetime > 0:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=periodic_task, trigger="interval", seconds=config.lifetime)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
# End of data updater setup ^^^

# Login manager setup vvv
class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(handle):
    if handle != config.username:
        return None
    user = User()
    user.id = handle
    return user

@login_manager.request_loader
def request_loader(request):
    handle = request.form.get('handle')
    if handle != config.username:
        return None
    user = User()
    user.id = handle
    return user

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    handle = request.form['handle']
    if handle == config.username and request.form['password'] == config.password:
        user = User()
        user.id = handle
        flask_login.login_user(user)
        log(f"Пользователь \"{handle}\" успешно вошел в систему")
        return redirect('/config/')
    log(f'Неудачная попытка входа для пользователя "{handle}"')
    return render_template('login.html', not_valid=True)

@app.route('/logout/')
@flask_login.login_required
def logout():
    log(f"Пользователь \"{flask_login.current_user.id}\" вышел из системы")
    flask_login.logout_user()
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Не авторизованы. <a href="/login/">Вход</a>', 401

# End of login setup ^^^

# Custom implementation of checking is mobile platform is used (because Flask3.x broke good implementation of Flask-Mobility)
@app.context_processor 
def utility_processor():
    return dict(is_mobile=True if re.match(r'.*Android.*|.*webOS.*|.*iPhone.*|.*iPad.*|.*iPod.*|.*BlackBerry.*|.*IEMobile.*|.*Opera Mini.*', request.headers.get('User-Agent')) else False)

# Render part vvv
@app.route('/')
def index():
    storage_data = storage.data
    if 'error' in storage_data:
        return render_template('render_index.html', message=storage_data['error'], config=config)
    return render_template('render_index.html', parallels=storage_data['settings']['klasses'].keys(), show=config.show, bells=pick_bells(config.bells), config=config)

@app.route('/get_rendered_parallel/', methods=['POST'])
def get_rendered_parallel():
    data = dict(request.json)
    if 'num' not in data:
        return 'Bad request. Endpoint requires "parallel" argument.', 400
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    return render_template('render_parallel.html', data=storage_data, cur_par=str(data['num']), short=True)

@app.route('/popup/', methods=['POST'])
def popup():
    data = dict(request.json)
    if 'klass' not in data or 'day' not in data:
        return 'Bad request. Endpoint requires "klass" and "day" arguments.', 400
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    return render_template('render_popup.html', klass=data['klass'], 
                           day=config.weekdays_short[data['day']] if data['day'] in config.weekdays_short else data['day'], 
                           data=storage_data['lessons'][data['klass']][data['day']], day_num=data['day'])

@app.route('/teachers/', methods=['GET'])
def get_teachers_list():
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    return render_template('render_teachers_list.html', teachers=storage_data['teachers'])

@app.route('/teachers/', methods=['POST'])
def get_teacher():
    data = dict(request.json)
    if 'teacher' not in data:
        return 'Bad request. Endpoint requires "teacher" argument.', 400
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    return render_template('render_teacher.html', data=storage_data, teacher=data['teacher'], short=True)

@app.route("/teacher_popup/", methods=['POST'])
def teacher_popup():
    data = dict(request.json)
    if 'teacher' not in data or 'day' not in data:
        return 'Bad request. Endpoint requires "teacher" and "day" arguments.', 400
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    return render_template('render_teacher_popup.html', teacher=data['teacher'], 
                           day=config.weekdays_short[data['day']] if data['day'] in config.weekdays_short else data['day'], 
                           data=storage_data['teachers'][data['teacher']][data['day']])

@app.route('/bells/')
def get_bells():
    return pick_bells(config.bells)

@app.route('/generate_iframe/')
@app.route('/generate_iframe/<int:days>/')
@app.route('/generate_iframe/<int:days>/<int:columns>/')
@app.route('/generate_iframe/<int:days>/<int:columns>/<int:skip>/')
def generate_iframe(days: int = config.iframe_days, columns: int = config.iframe_columns, skip: int = 0, render_to_user: bool = True):
    storage_data = storage.data
    if 'error' in storage_data:
        return f'Internal server Error. Something happened during getting data. Error: {storage_data["error"]}', 500
    try:
        data = storage.prepare_iframe_data(days, columns, skip)
    except Exception as ex:
        if render_to_user:
            return f'Something went wrong during generating iframe. Exception: {ex}', 500
        else:
            raise ex
    return render_jinja('src/templates', 'render_iframe.html', data=data, config=config, time=datetime.now())

@app.route('/download_iframe/')
@app.route('/download_iframe/<int:days>/')
@app.route('/download_iframe/<int:days>/<int:columns>/')
@app.route('/download_iframe/<int:days>/<int:columns>/<int:skip>/')
def download_iframe(days: int = config.iframe_days, columns: int = config.iframe_columns, skip: int = 0, render_to_user: bool = True):
    data = generate_iframe(days, columns, skip, True)
    if type(data) == tuple:
        return data
    try:
        with open(f'{ROOT_DIR}/data/tmp/index.html', 'w') as f:
            f.write(data)
    except Exception as ex:
        return f'Error occured while saving file to temporary folder. Error: {ex}', 500
    else:
        try:
            return send_file(f'{ROOT_DIR}/data/tmp/index.html', as_attachment=True, download_name='index.html')
        except Exception as ex:
            return f'Error occured while sending file to user. Error: {ex}', 500


def save_iframe(days: int = config.iframe_days, columns: int = config.iframe_columns, skip: int = 0):
    if not config.save_iframe:
        return '"Save iframe" setting is set to False. Iframe will not be saved', 400
    if not config.iframe_file:
        return 'Path to iframe file is not specified or specified incorrectly. Iframe will not be saved', 400
    try:
        iframe = generate_iframe(days, columns, skip, render_to_user=False)
    except Exception as ex:
        return f'Something went wrong during generating of iframe file. Error: {ex}', 500
    try:
        with open(config.iframe_file, 'w') as f:
            f.write(iframe)
    except Exception as ex:
        return f'Something went wrong during saving of iframe file. Error: {ex}', 500
    return f'OK. Iframe saved to: "{config.iframe_file}"', 200

@app.route('/update/')
def update_url():
    if not config.is_setup:
        return 'The server is configured incorrectly or is not configured. Contact your system administrator before using this method', 400
    status = 200
    try:
        res = storage.update_data()[0]
    except Exception as ex:
        res = f'Error occured while updating data: {ex}'
        status = 500
    if config.save_iframe:
        res += '<br>'
        try:
            res += save_iframe()[0]
        except Exception as ex:
            res += f'Error occured while saving iframe: {ex}'
            status = 500
    return res, status

@app.route('/carousel/', methods=['GET'])
def carousel_init():
    if config.carousel:
        return {
            "file": carousel(0,0)
        }
    return abort(400, 'Карусель отключена')

@app.route('/carousel/', methods=['POST'])
def carousel_data():
    data = dict(request.json)
    if config.carousel:
        return {
            "file": carousel(int(data['step']), carousel.index(data['current']))
            }
    return abort(400, 'Карусель отключена')

@app.route('/carousel/<string:path>/')
def carousel_file(path: str):
    if config.carousel:
        return send_file(carousel.dir_abs_path+'/'+path)
    return abort(400, 'Карусель отключена')
# End of render part ^^^

# Web-Config part
@app.route('/config/')
@flask_login.login_required
def config_url():
    return render_template('config_config.html', program_info=config.program_info, config=config)

@app.route('/config/save_config/', methods=['POST'])
@flask_login.login_required
def save_config_url():
    try:
        data = dict(request.json)
        config.write_config_from_dict(data)
        log("Сохранена новая конфигурация.")
        return '<p>Данные успешно сохранены.<br>Рекомендуется перезагрузить сервер.</p>', 200
    except Exception as ex:
        log.error(f'Произошла ошибка при сохранении новой конфигурации. Ошибка: {ex}')
        return f'<p>При сохранении данных что-то пошло не так. Ошибка: {ex}</p>', 500
    
@app.route('/upload/', methods=['GET'])
@flask_login.login_required
def upload_render():
    return render_template('config_upload.html', program_info=config.program_info, config=config)

@app.route('/upload/', methods=['POST'])
@flask_login.login_required
def upload():
    if not config.is_setup:
        return 'The server is configured incorrectly or is not configured. Contact your system administrator.', 500
    if 'file' not in request.files:
        return render_template('config_upload.html', program_info=config.program_info, config=config, error='Файл не выбран')
    file = request.files['file']
    if file.filename[file.filename.rfind('.'):] not in ['.xlsx', '.xls', '.ods']:
        return render_template('config_upload.html', program_info=config.program_info, config=config, error=f'Данный формат файла не поддерживается. Используйте формат .xlsx ; .xls ; .ods')
    if re.match(r'\d\d[\_\.\-]\d\d[\_\.\-]\d{4}\.(xls)?(xlsx)?(ods)?', file.filename) is None:
        return render_template('config_upload.html', program_info=config.program_info, config=config, error=f'Некорректное имя файла. Пожалуйста, назовите файл следующим образом: день-месяц-год.расширение  Пример: 12-03-2024.xlsx')
    try:
        file.save(config.directory+file.filename)
        log(f'Файл "{config.directory+file.filename}" загружен.')
        update_res = storage.update_data()
        if update_res[1]:
            return render_template('config_upload.html', program_info=config.program_info, config=config, error=f'Произошла ошибка при обновлении данных. Ошибка: {update_res[0]}')
        else:
            return render_template('config_upload.html', program_info=config.program_info, config=config, uploaded=True)
    except Exception as ex:
        log.error(f'Произошла ошибка при сохранении файла. Ошибка: {ex}')
        return render_template('config_upload.html', program_info=config.program_info, config=config, error=f'Произошла ошибка при сохранении файла. Ошибка: {ex}')

@app.route('/carousel_edit/', methods=['GET'])
@flask_login.login_required
def upload_carousel_render():
    return render_template('config_upload_carousel.html', images=carousel.files, program_info=config.program_info, config=config)

@app.route('/carousel_edit/', methods=['POST'])
@flask_login.login_required
def upload_carousel():
    if 'file' not in request.files:
        return abort(400, 'Файл не загружен')
    errors = []
    for file in request.files.getlist('file'):
        if file.filename[file.filename.rfind('.')+1:] not in carousel.allowed_extensions:
            errors.append(f'Ошибка при загрузке "{file.filename}" - тип файла не поддерживается.')
            continue
        try:
            file.save(config.carousel_directory+file.filename)
            carousel.append(file.filename)
            carousel.sort()
            log(f'Файл карусели "{config.carousel_directory+file.filename}" загружен.')
        except FileExistsError as ex:
            log.warning(f'Загружаемый файл карусели "{file.filename}" уже существует.')
            errors.append(f'Ошибка при загрузке "{file.filename}" - файл уже существует.')
        except Exception as ex:
            log.error(f'Произошла ошибка при сохранении файла карусели "{config.carousel_directory+file.filename}". Ошибка: {ex}')
            errors.append(f'Ошибка при загрузке "{file.filename}" - произошла непредвиденная ошибка {ex}.')
    if len(errors) == 0:
        return 'Ok'
    return abort(400, 'Ошибки:\n'+"\n".join(errors))

@app.route('/carousel_edit/remove/<string:path>/', methods=['GET'])
@flask_login.login_required
def upload_carousel_remove(path):
    try:
        carousel.remove(path)
    except ValueError:
        log.warning(f'Неудачная попытка удалить несуществующий файл карусели "{path}"')
        return abort(400, f'Файл "{path}" не существует.')
    except Exception as ex:
        log.error(f'Произошла непредвиденная ошибка при удалении файла карусели "{path}" из объекта carousel. Ошибка: {ex}')
        return abort(500, f'Произошла непредвиденная ошибка при удалении файла карусели "{path}" из объекта carousel. Ошибка: {ex}')
    try:
        os.remove(carousel.dir_abs_path+'/'+path)
    except Exception as ex:
        log.error(f'Произошла непредвиденная ошибка при удалении файла карусели "{path}". Ошибка: {ex}')
        return abort(500, f'Произошла непредвиденная ошибка при удалении файла карусели "{path}". Ошибка: {ex}')
    log(f'Файл карусели "{carousel.dir_abs_path+"/"+path}" успешно удален.')
    return 'Ok'

@app.route('/carousel_edit/<string:path>/', methods=['GET'])
@flask_login.login_required
def upload_carousel_images(path: str):
    return send_file(carousel.dir_abs_path+'/'+path)

@app.route('/carousel_edit/send/<string:path>/', methods=['GET'])
@flask_login.login_required
def upload_carousel_images_send(path: str):
    return send_file(carousel.dir_abs_path+'/'+path, as_attachment=True, download_name=path)

@app.route('/custom_iframe/', methods=['GET'])
@flask_login.login_required
def custom_iframe_render():
    return render_template('config_custom_iframe.html', program_info=config.program_info, config=config)

@app.route('/save_iframe/')
@app.route('/save_iframe/<int:days>/')
@app.route('/save_iframe/<int:days>/<int:columns>/')
@app.route('/save_iframe/<int:days>/<int:columns>/<int:skip>/')
@flask_login.login_required
def save_iframe_view(days: int = config.iframe_days, columns: int = config.iframe_columns, skip: int = 0):
    log('Iframe сохранен.')
    return save_iframe(days, columns, skip)

@app.route("/get_tools/")
@flask_login.login_required
def get_tools():
    return render_template('config_tools.html', config=config, del_files=get_filenames(config.directory))

@app.route("/cfg_change_psswd/", methods=['GET'])
@flask_login.login_required
def chng_psswd_view():
    return render_template('config_psswd_change.html')

@app.route("/cfg_change_psswd/", methods=['POST'])
@flask_login.login_required
def chng_psswd():
    if request.form['password'] == config.password and request.form['password_new'] == request.form['password_new_check'] != request.form['password']:
        flask_login.logout_user()
        config.password = request.form['password_new']
        config.write_config()
        log.warning("Изменен пароль!")
        return redirect('/config/')
    log.warning("Неудачная попытка изменения пароля!")
    return render_template('config_psswd_change.html', not_valid=True)


@app.route('/download/<string:arg>/')
@flask_login.login_required
def download_data(arg: str):
    if arg == 'logs':
        log('Отправление файла логов')
        return send_file(ROOT_DIR+'/'+config.log_filename, as_attachment=True, download_name='log.txt')
    if arg == 'logs-100':
        log('Отправление последних 100 строк лога')
        with open(config.log_filename, 'r', encoding='utf-8') as f:
            return '<br>'.join(f.readlines()[-100:])
    if arg == 'current':
        log('Отправление файла с текущими данными')
        try:
            f = open(config.directory+get_filenames(config.directory)[0], 'rb')
        except FileNotFoundError:
            return abort(404)
        except Exception as ex:
            return f'Error: {ex}', 500
        data = f.read()
        f.close()
        return send_file(
            io.BytesIO(data), as_attachment=True, download_name=get_filenames(config.directory)[0]
        )
    if arg == 'current-json':
        log('Отправление текущих данных в формате json')
        return send_file(
                io.BytesIO(json.dumps(storage.data).encode('utf-8')), as_attachment=True, download_name='data.json'
            )
    if arg == 'example':
        log('Отправление файла примера данных')
        try:
            f = open('data/example/'+get_filenames('data/example/')[0], 'rb')
        except FileNotFoundError:
            return abort(404)
        except Exception as ex:
            return f'Error: {ex}', 500
        data = f.read()
        f.close()
        return send_file(
            io.BytesIO(data), as_attachment=True, download_name=get_filenames(config.directory)[0]
        )
    
@app.route('/logs-clear/')
@flask_login.login_required
def clear_logs():
    with open(config.log_filename, 'w') as f:
        f.write('---\n')
    log.warning("Произведена очистка лога")
    return 'Файл лога успешно очищен'

@app.route('/custom_function/', methods=['POST'])
@flask_login.login_required
def custom_function():
    data = dict(request.json)
    if data['name'] not in config.custom_functions:
        return "Функция не найдена", 400
    try:
        res = subprocess.run(config.custom_functions[data['name']]['cmd'], capture_output=True, shell=True, text=True)
        if res.returncode == 0:
            log(f'Кастомная функция "{data["name"]}" выполнилась успешно')
            return "<code>"+str(res.stdout)+"</code>", 200
        else:
            log.warning(f'Что то пошло не так при выполнении кастомной функции "{data["name"]}". Ошибка: {str(res.stderr)}')
            return "<code>"+str(res.stderr)+"</code>", 500
    except Exception as ex:
        log.error(f'При попытке запуска кастомной функции проищошла непредвиденная ошибка. Ошибка: {ex}')
        return f"Произошла непредвиденная ошибка. Ошибка: {ex}", 500
    
@app.route('/cfg_add_custom_function/', methods=['GET'])
@flask_login.login_required
def cfg_add_custom_function_view():
    return render_template('cfg_add_custom_function.html', config=config)

@app.route('/cfg_add_custom_function/', methods=['POST'])
@flask_login.login_required
def cfg_add_custom_function():
    f_name = request.form['name']
    f_desc = request.form['desc']
    f_cmd = request.form['cmd']
    if f_name.strip() == '':
        return render_template('cfg_add_custom_function.html', error='Имя функции обязательно!', config=config)
    if f_desc.strip() == '':
        f_desc = None
    if f_cmd.strip() == '':
        return render_template('cfg_add_custom_function.html', error='Код скрипта обязателен!', config=config)
    if f_name in config.custom_functions.keys():
        return render_template('cfg_add_custom_function.html', error='Функция с таким именем уже существует!', config=config)
    config.custom_functions[f_name] = {
        'cmd': f_cmd,
        'description': f_desc
    }
    log(f'Добавлена кастомная функция "{f_name}", описание - "{f_desc}"')
    config.write_config()
    return render_template('cfg_add_custom_function.html', uploaded=True, config=config)

@app.route('/cfg_remove_custom_function/', methods=['GET'])
@flask_login.login_required
def cfg_remove_custom_function_view():
    return render_template('cfg_remove_custom_function.html', config=config)

@app.route('/cfg_remove_custom_function/<string:name>/', methods=['GET'])
@flask_login.login_required
def cfg_remove_custom_function(name: str):
    if name in config.custom_functions.keys():
        del config.custom_functions[name]
        log(f'Удалена кастомная функция "{name}"')
        config.write_config()
        if len(config.custom_functions.keys()) == 0:
            return redirect('/config/')
        return render_template('cfg_remove_custom_function.html', config=config)
    else:
        return render_template('cfg_remove_custom_function.html', error="Функции с таким именем не существует", config=config)
    
@app.route('/cfg_remove_old_files/')
@flask_login.login_required
def cfg_remove_old_files():
    files = get_filenames(config.directory)[1:]
    for file in files:
        os.remove(config.directory+file)
    log(f'Старые файлы с расписанием успешно очищены ({"; ".join(files)})')
    return redirect('/config/')

@app.route('/cfg_remove_all_files/')
@flask_login.login_required
def cfg_remove_all_files():
    files = get_filenames(config.directory)
    for file in files:
        os.remove(config.directory+file)
    log.warning(f'Очищены все файлы с расписанием: ({"; ".join(files)})')
    return redirect('/config/')

@app.route('/time/')
def server_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')