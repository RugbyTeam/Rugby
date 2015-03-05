from rugby_state import RugbyState
import config

import sqlite3
import logging
import os

logger = logging.getLogger(config.LOGGER_NAME)

class RugbyDatabase:
    def __init__(self, rugby_root):
        """
        timestamp of head commit
        timestamp of build finish
        author[login, email, avatar]
        commit_url
        contributors emails
        commit_id
        commit_message
        state
        """
        self.db_path = os.path.join(rugby_root, 'rugby.db')
        self._execute("""CREATE TABLE IF NOT EXISTS builds(commit_id TEXT PRIMARY KEY,
                                                           commit_message TEXT,
                                                           commit_url TEXT,
                                                           state TEXT,
                                                           commit_timestamp TEXT,
                                                           finish_timestamp TEXT,
                                                           author_login TEXT,
                                                           author_email TEXT,
                                                           author_avatar_url TEXT,
                                                           contributors_email TEXT)""")

    def _execute(self, query):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        # Escape single quotes
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
        except Exception:
            logger.debug('Could not execute query')
            logger.debug('COULD NOT EXECUTE QUERY:  %s' % query)
            raise
        connection.close()
        return result
    
    def insert_build(self, build_info):
        commit_message = build_info.commit_message.replace('\'', '\'\'')
        values = (build_info.commit_id,
                  build_info.commit_message,
                  build_info.commit_url,
                  str(RugbyState.INITIALIZING),
                  build_info.commit_timestamp,
                  build_info.finish_timestamp,
                  build_info.author_login,
                  build_info.author_email,
                  build_info.author_avatar_url,
                  build_info.contributors_email)
        try:
            self._execute("""INSERT INTO builds VALUES('%s', '%s', '%s', '%s', '%s', 
                                                       '%s', '%s', '%s', '%s', '%s')""" % values)
        except sqlite3.IntegrityError:
            logger.debug('Could not record build, commit_id already exists')

    def update_build(self, commit_id, state):
        self._execute("UPDATE builds SET state = '%s' WHERE commit_id = '%s'" % (state, commit_id))

    def get_builds(self):
        return self._execute("SELECT * FROM builds")
 
