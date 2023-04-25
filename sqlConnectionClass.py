# class SqlConnection:
#     def __init__(self):
#         self.connection = None
#
#     def establishConnection(self, connection):
#         self.connection = connection
#
#     def returnConnection(self):
#         return self.connection

class Columns:
    def __init__(self):
        self.columns = []

    def storeColumns(self, columns):
        self.columns = columns

    def returnColumns(self):
        return self.columns