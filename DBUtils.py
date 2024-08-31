import pymysql

class DBUtils:
    @staticmethod
    def test():
        db = DBUtils()
        pass

    def __init__(self):
        pass

    connection = None

    def tryConnect(self):
        if self.connection is None:
            self.connection = pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='tk1372353',
                db='immortal',
                charset='utf8',
            )
        return self.connection

    def close(self):
        if self.connection is not None:
            self.connection.close()
        return

    # result format tuple ((1,2,3...),()...)
    def doQuery(self, sql):
        connect = self.tryConnect()
        with connect.cursor() as cursor:
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
            except Exception as ex:
                print(f'debug sql: {sql}')
                raise ex
        return result

    def doCommand(self, sql):
        connect = self.tryConnect()
        with connect.cursor() as cursor:
            cursor.execute(sql)
        connect.commit()

    def doCommands(self, sqllist):
        connect = self.tryConnect()
        for sql in sqllist:
            with connect.cursor() as cursor:
                cursor.execute(sql)
        connect.commit()


if __name__ == '__main__':
    DBUtils.test()
