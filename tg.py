from mariadb import Connection, Cursor


class Tg:
    connection = None  # type: Connection
    cursor = None  # type: Cursor
    id = ''  # type: str
    channel_id = ''  # type: str
    message_id = ''  # type: str
    message_file = ''  # type: str
    message_text = ''  # type: str

    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def get_by_id(self, id):
        query = "SELECT * FROM tg WHERE id = ?"
        self.cursor.execute(query, (id,))
        row = self.cursor.fetchone()
        self.id = row[0]
        self.channel_id = row[1]
        self.message_id = row[2]
        self.message_file = row[3]
        self.message_text = row[4]

    def check_duplicate(self, channel_id, message_id):
        query = "SELECT * FROM tg WHERE channel_id = ? AND message_id = ?"
        self.cursor.execute(query, (channel_id,message_id))
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False
        else:
            return True
