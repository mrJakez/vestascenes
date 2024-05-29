import sqlite3
import uuid
import datetime


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]




class Repository(metaclass=SingletonMeta):
    _connection = None
    def get_connection(self):
        if self._connection is None:
            print("connection will be initialized")
            self._connection = sqlite3.connect("/database/vbcontrol.db", check_same_thread=False)

        return self._connection
    def get_snapshots(self):
        con = self.get_connection()
        cursor = con.cursor()

        sqlite_select_query = 'SELECT * from snapshots'
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        return records

    def get_chatgpt_history(self):
        con = self.get_connection()
        cursor = con.cursor()

        sqlite_select_query = 'SELECT * from chatgpt_history'
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()

        list = []
        for record in records:
            list.append({
                'id': record[0],
                'created_at': record[1],
                'role': record[2],
                'content': record[3]
            })

        return list


    def save_chatgpt_history(self, obj):
        con = self.get_connection()
        cursor = con.cursor()
        sql = 'INSERT INTO chatgpt_history(id, created_at, role, content) VALUES(?,?,?,?)'
        cursor.execute(sql, (str(uuid.uuid4()), datetime.datetime.now(), obj['role'], obj['content']))
        con.commit()


    def get_scene_instances(self):
        con = self.get_connection()
        cursor = con.cursor()

        sqlite_select_query = 'SELECT * from scene_instances'
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("get_scene_instances -> total rows are:  ", len(records))

        list = []
        for record in records:
            list.append({
                'id': record[0],
                'raw': record[1],
                'class_string': record[2],
                'start_date': record[3],
                'end_date': record[4],
                'priority': record[5],
                'is_active': record[6]
            })

        return list

    def save_scene_instance(self, obj):
        con = self.get_connection()
        cursor = con.cursor()
        sql = 'INSERT INTO scene_instances(id, raw, class_string, start_date, end_date, priority, is_active) VALUES(?,?,?,?,?,?,?)'
        cursor.execute(sql, (obj['id'], obj['raw'], obj['class_string'], obj['start_date'], obj['end_date'], obj['priority'], obj['is_active']))
        con.commit()


    def scene_instances_with_id_exists(self, id) -> bool:
        con = self.get_connection()
        cursor = con.cursor()
        sql = f"SELECT * FROM scene_instances WHERE id = '{id}'"
        cursor.execute(sql)
        records = cursor.fetchall()

        if len(records) == 0:
            return False
        else:
            return True


    def get_active_scene_instance(self):
        con = self.get_connection()
        cursor = con.cursor()
        sql = 'SELECT * FROM scene_instances WHERE is_active = 1'
        cursor.execute(sql)
        records = cursor.fetchall()

        if len(records) == 0:
            return None

        record = records[0]
        return {
                'id': record[0],
                'raw': record[1],
                'class_string': record[2],
                'start_date': record[3],
                'end_date': record[4],
                'priority': record[5],
                'is_active': record[6]
            }

    def unmark_active_scene_instance(self):
        con = self.get_connection()
        cursor = con.cursor()
        sql = 'UPDATE scene_instances SET is_active = 0 WHERE is_active = 1'
        cursor.execute(sql)





