import sqlite3


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
        print("get_connection() triggered")

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
        print("Total rows are:  ", len(records))
        return records

    def get_snapshot_object(self, record):

        raw = record[1]

        list = []
        # raw is a list of 6 lists as string. We have to convert this one towards a List(List(Int)) object
        for item in raw.split('],['):
            item = item.replace('[', '').replace(']', '')
            item = item.split(',')
            item = [int(numeric_string) for numeric_string in item]
            list.append(item)

        return {"title": record[0], "raw":list}

