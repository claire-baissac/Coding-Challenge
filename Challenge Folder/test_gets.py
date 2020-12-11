"""This module has the functions that get data from the database"""

import logging as log
from pandas import DataFrame

from test_database import (
    execute_queries_get_dataframes,
    exc_qrs_get_dfs)

log.basicConfig(level=log.DEBUG)
log.info('----- QRS_GETS.PY -----')

def get_table(person=None, count=0, con=None):
    """Gets all data needed to display map from the desk being scanned.

    Args:
        person=None (str): determines the name by which to filter the records table
        count=0 (int): the number of results to return

    Return:
        response_object (obj): python object of returned dataframes of the following:
            "users_table" (df)
            "data_table" (df)"""

    try:
        # get the user data
        query_select_records = ("SELECT * FROM records WHERE person =\'" + str(person) + "\'")
        record_list = exc_qrs_get_dfs([query_select_records], con)

        log.info("database responses: %s", record_list)
        rec_list = record_list[0].values.tolist()
        data_id = [row[2] for row in rec_list]
        t = tuple(data_id)

        # get the data given the user ids
        query_select_data = ("SELECT * FROM data WHERE id IN {} LIMIT {}".format(t, count))
        data_list = exc_qrs_get_dfs([query_select_data], con)

        response_object = {
            "records_table":record_list[0],
            "data_table": data_list[0]}

    except Exception as error:
        log.info(error)
        return error

    return response_object
