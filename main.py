from flask import Flask, render_template, request, redirect, url_for
from config_handler import Config
from pathlib import Path
from datetime import datetime
import json
import mysql.connector
from tg import Tg
import subprocess

app = Flask(__name__)
config = Config()
try:
    mysql_connection = mysql.connector.connect(
        user=config.get('database user'),
        password=config.get('database password'),
        host=config.get('database address'),
        port=int(config.get('database port')),
        database=config.get('Database name')
    )
    cursor = mysql_connection.cursor()
except mysql.connector.Error as e:
    print(f"Error connecting to Mysql Platform: {e}")
    exit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tg/list')
def tg_list():
    cursor.execute('SELECT * FROM tg LIMIT 10')
    files = cursor.fetchall()
    return render_template('tg_list.html', files=files)


@app.route('/tg/download/<id>')
def tg_download(id):
    cursor.execute('SELECT * FROM tg WHERE id = %s', (id,))
    file = cursor.fetchone()
    message_url = "https://t.me/c/{}/{}".format(file[1], file[2])
    file_name = file[4] or file[3]
    # tdl download -n 1 -u https://t.me/c/1783815989/832 --template "[Nigel] Vlad Love - 04 [720p][D2F8C20B].mkv"
    process = subprocess.Popen(
        ['tdl', 'download', '-n', '1', '-u', message_url, '--template', file_name],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    while (line := process.stdout.readlines()) != '':
        if len(line) > 0:
            cursor.execute('UPDATE tg SET status = %s WHERE id = %s', (str(line), id))
            mysql_connection.commit()
            print(line)
    return redirect(url_for('tg_list'))

@app.route('/import/tg', methods=['GET', 'POST'])
def import_tg():
    if request.method == 'GET':
        return render_template('import_tg.html')
    elif request.method == 'POST':
        # These messages will be shown in the template
        messages = []
        tg = Tg(mysql_connection, cursor)
        # Get and Create folder for uploaded json files
        json_folder = Path().cwd().joinpath(config.get('Json Folder'))
        json_folder.mkdir(exist_ok=True, parents=True)
        for item in request.files.getlist('json'):
            if item.filename != '' and item.filename.endswith('.json'):
                filename = datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f-") + item.filename
                item.save(json_folder.joinpath(filename))
                messages.append(('success', 'File {} uploaded successfully'.format(filename)))
            else:
                messages.append(('danger', 'No file uploaded, or file "{}" not allowed'.format(item.filename)))

        json_files = json_folder.rglob('*.json')
        for item in json_files:
            data = json.loads(item.read_text(encoding='utf-8'))  # type: dict

            if data.get('id') is None:
                messages.append(('danger', 'File {} dose not have proper json data '.format(item.name)))
            else:
                # Queries that will be used here
                # check_query = ("SELECT * FROM tg WHERE `channel_id` = ? AND `message_id` = ?")
                insert_query = ("INSERT INTO tg (`channel_id`, `message_id`, `message_file`, `message_text`) "
                                "VALUES (%s, %s, %s, %s)")
                channel_id = str(data.get('id'))
                for tg_msg in data.get('messages'):  # type: dict
                    message_id = tg_msg.get('id')
                    message_file = tg_msg.get('file')
                    message_text = tg_msg.get('text') or 'Empty'
                    # check if the message exists in the database
                    if tg.check_duplicate(channel_id, message_id) == 0:
                        cursor.execute(insert_query, (channel_id, message_id, message_file, message_text))

                mysql_connection.commit()
                messages.append(('success', 'File {} imported successfully'.format(item.name)))
            item.unlink()
        return render_template('import_tg.html', messages=messages)


@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'GET':
        return render_template('setting.html', config=config)
    elif request.method == 'POST':
        for key, value in request.form.items():
            config.set(key, value)
        config.update()
        return redirect(url_for('setting'))


if __name__ == '__main__':
    app.run(debug=True)