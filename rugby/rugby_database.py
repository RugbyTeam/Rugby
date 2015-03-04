from rugby_state import RugbyState
import config

import sqlite3
import logging
import os

logger = logging.getLogger(config.LOGGER_NAME)

class RugbyDatabase:
    def __init__(self, rugby_root):
        self.db_path = os.path.join(rugby_root, 'rugby.db')
        self._execute("""CREATE TABLE IF NOT EXISTS builds(commit_id TEXT PRIMARY KEY,
                                                           commit_message TEXT,
                                                           state TEXT)""")

    def _execute(self, query):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
        except Exception:
            logger.debug('Could not execute query')
            raise
        connection.close()
        return result
    
    def insert_build(self, commit_id, commit_message):
        try:
            self._execute("INSERT INTO builds VALUES('%s', '%s', '%s')" % (commit_id, commit_message, str(RugbyState.INITIALIZING)))
        except sqlite3.IntegrityError:
            logger.debug('Could not record build, commit_id already exists')

    def update_build(self, commit_id, state):
        self._execute("UPDATE builds SET state = '%s' WHERE commit_id = '%s'" % (state, commit_id))

    def get_builds(self):
        return self._execute("SELECT * FROM builds")
 

        
