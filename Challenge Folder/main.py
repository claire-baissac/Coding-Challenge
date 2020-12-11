"""This module is called by Google App Engine

It looks for "app" in the "main.py" class to run flask with gunicorn"""

import time
import logging
from pandas import DataFrame
from flask import Flask, render_template, request
from flask.logging import create_logger
from test_dbconfig import get_db_kwargs
import psycopg2 as pg
import test_gets as gets
import constants

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
log = create_logger(app)
log.info('------ DEBUG LOGGING STARTS HERE -------')

@app.route('/', methods=['GET'])
def index():
    """Runs when GET requested on '/'.

    Returns:
        render_template (flask): index.html
    """
    log.info("@ index()")

    return render_template(
        'at-index.html')


#this is not in use
@app.route('/log', methods=['GET'])
def at_log():
    """Runs when GET requested on '/log'.

    When user selects view log from the home page.

    Return:
        render_template (flask): html template based on logic from this app
    """
    log.info("@ at_log()")

    response = gets.get_table()
    if isinstance(response, Exception):
        return render_template('at-error.html', message=".error('Error occured')", error=response)
    database_log_html = response["data_table"].to_html(index=False)

    return render_template(
        'at-log.html',
        data=database_log_html)


@app.route('/test/<int:item_count>', methods=['GET'])
def at_test(item_count=None):
    """Runs when GET requested on '/login/<user_id>'.

    The main endpoint to test the time it takes to process the items in the database.

    Args:
        item_count=None (str): sets the number of items to count after the '/test/' path

    Return:
        render_template (flask): html template based on logic from this app"""

    DB_KWARGS = get_db_kwargs()

    DB_KWARGS_TEXT = {
        "user":"challenge_role",
        "password":"this-is-not-the-real-password",
        "dbname":"test_db",
        "host":"34.84.42.175"
    }

    try:
        # connect to the server
        con = None
        con = pg.connect(**DB_KWARGS_TEXT)
        log.info("@ at_test(item_count=None): %s", item_count)

        #  ˅This is the script that measures the performance, not allowed to edit this section.˅
        hit_time = time.time()
        #  ˄This is the script that measures the performance, not allowed to edit this section.˄

        # validate API key
        auth = request.args.get('authorisation')
        if auth != constants.API_KEY:
            return render_template(
                'at-error.html',
                message="Invalid Access Key",
                error=403)

        # <- get query string
        person_query = request.args.get('person', type = str)
        type_query = request.args.get('type', type = str)
        response = gets.get_table(person_query, item_count, con)

        if isinstance(response, Exception):
            return render_template('at-error.html', message="There was an error.", error=response)

        records_json = response["records_table"].to_json(orient="records")
        data_json = response["data_table"].to_json(orient="records")

        if item_count > 100:
            return render_template(
                'at-error.html',
                message="More then 100 items selected, too many. Item Count: ",
                error=item_count)

        if (type_query == "text"):
            return render_template(
                'at-text.html',
                records=records_json,
                data=data_json,
                item_count=item_count,
                hit=hit_time)

        return render_template(
            'at-json.html',
            records=records_json,
            data=data_json,
            item_count=item_count,
            hit=hit_time)

    except pg.Error as error:
        return error

    finally:
        if con is not None:
            con.close()

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google app
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # app Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)
