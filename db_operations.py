from db_connection import DatabaseConnection



class DatabaseOperations:

    def __init__(self, connection_string):

        self.db = DatabaseConnection(connection_string)

        self.db.connect()



    def __del__(self):

        self.db.disconnect()



    # 图书管理相关操作

    def get_all_books(self):

        query = "SELECT * FROM books"

        return self.db.execute_query(query)



    def get_book_by_id(self, book_id):

        query = "SELECT * FROM books WHERE 索书号 = %s"

        result = self.db.execute_query(query, (str(book_id),))

        return result[0] if result else None



    def add_book(self, book_data):

        query = """

        INSERT INTO books (索书号, 书名, 作者, 出版社, 类别id, 总数, 在库数量)

        VALUES (%s, %s, %s, %s, %s, %s, %s)

        """

        params = (

            book_data['索书号'], book_data['书名'], book_data['作者'],

            book_data['出版社'], book_data['类别id'], book_data['总数'], book_data['在库数量']

        )

        return self.db.execute_query(query, params)



    def update_book(self, book_data):
    # 调用存储过程更新图书信息
      return self.db.execute_procedure('update_book_proc', [
        str(book_data['索书号']),
        book_data['书名'],
        book_data['作者'],
        book_data['出版社'],
        book_data['类别id'],
        book_data['总数'],
        book_data['在库数量']
      ])



    def delete_book(self, book_id):
        try:
            check_query = "SELECT 总数, 在库数量 FROM books WHERE 索书号 = %s"
            book = self.db.execute_query(check_query, (str(book_id),))
            if not book:
                print("删除失败：图书不存在")
                return None
            if book[0]['总数'] != book[0]['在库数量']:
                print("删除失败：图书仍有借出，无法删除")
                self.db.rollback()
                return None
            
            delete_query = "DELETE FROM books WHERE 索书号 = %s"
            result = self.db.execute_query(delete_query, (str(book_id),))
            self.db.commit()
            return result
        except Exception as e:
            print(f"删除图书时出错: {e}")
            self.db.rollback()
            return None



    # 读者管理相关操作

    def get_all_readers(self):

        query = "SELECT * FROM readers"

        return self.db.execute_query(query)



    def get_reader_by_id(self, reader_id):

        query = "SELECT * FROM readers WHERE 读者卡号 = %s"

        result = self.db.execute_query(query, (str(reader_id),))

        return result[0] if result else None



    def add_reader(self, reader_data):

        query = """

        INSERT INTO readers (读者卡号, 姓名, 证件号)

        VALUES (%s, %s, %s)

        """

        params = (reader_data['读者卡号'], reader_data['姓名'], reader_data['证件号'])

        return self.db.execute_query(query, params)



    def update_reader(self, reader_data):
    # 调用存储过程更新读者信息
      return self.db.execute_procedure('update_reader_proc', [
        str(reader_data['读者卡号']),
        reader_data['姓名'],
        reader_data['证件号']
      ])



    def delete_reader(self, reader_id):
        try:
            check_query = "SELECT COUNT(*) AS 借阅数量 FROM borrow_records WHERE 读者卡号 = %s AND 归还日期 IS NULL"
            borrow = self.db.execute_query(check_query, (str(reader_id),))
            if borrow[0]['借阅数量'] > 0:
                print("删除失败：读者还有未归还图书，无法删除")
                self.db.rollback()
                return None

            delete_query = "DELETE FROM readers WHERE 读者卡号 = %s"
            result = self.db.execute_query(delete_query, (str(reader_id),))
            self.db.commit()
            return result
        except Exception as e:
            print(f"删除读者时出错: {e}")
            self.db.rollback()
            return None



    # 借阅管理相关操作

    def borrow_book(self, reader_id, book_id):

        # 调用借书存储过程，确保参数被正确处理为字符串类型

        return self.db.execute_procedure('borrow_book', (str(reader_id), str(book_id), '@p_success', '@p_message'))



    def return_book(self, borrow_id):

        # 调用还书存储过程，确保参数被正确处理为字符串类型

        return self.db.execute_procedure('return_book', (str(borrow_id), '@p_success', '@p_message', '@p_fine_amount'))



    def renew_book(self, borrow_id):

        # 调用续借存储过程，确保参数被正确处理为字符串类型

        return self.db.execute_procedure('renew_book', (str(borrow_id), '@p_success', '@p_message', '@p_new_due_date'))



    def get_reader_borrow_history(self, reader_id):

        # 调用查询读者借阅历史的存储过程，确保参数被正确处理为字符串类型

        return self.db.execute_procedure('get_reader_borrow_history', (str(reader_id),))



    def get_all_borrow_records(self):

        query = "SELECT * FROM borrow_records"

        return self.db.execute_query(query)



    def get_borrow_record_by_id(self, borrow_id):

        query = "SELECT * FROM borrow_records WHERE 借阅记录编号 = %s"

        result = self.db.execute_query(query, (str(borrow_id),))

        return result[0] if result else None



    # 罚款管理相关操作

    def get_all_fines(self):

        query = "SELECT * FROM fines"

        return self.db.execute_query(query)



    def get_fine_by_borrow_id(self, borrow_id):

        query = "SELECT * FROM fines WHERE 借阅记录编号 = %s"

        result = self.db.execute_query(query, (str(borrow_id),))

        return result[0] if result else None



    def add_fine(self, fine_data):

        query = """

        INSERT INTO fines (借阅记录编号, 罚款金额)

        VALUES (%s, %s)

        """

        params = (str(fine_data['借阅记录编号']), fine_data['罚款金额'])

        return self.db.execute_query(query, params)



    # 类别管理相关操作

    def get_all_categories(self):

        query = "SELECT * FROM categories"

        return self.db.execute_query(query)



    def add_category(self, category_name):

        query = "INSERT INTO categories (类别名称) VALUES (%s)"

        return self.db.execute_query(query, (category_name,))



    # 出版社管理相关操作

    def get_all_publishers(self):

        query = "SELECT * FROM publishers"

        return self.db.execute_query(query)



    def add_publisher(self, publisher_data):

        query = """

        INSERT INTO publishers (名称, 地址, 联系电话)

        VALUES (%s, %s, %s)

        """

        params = (publisher_data['名称'], publisher_data['地址'], publisher_data['联系电话'])

        return self.db.execute_query(query, params)



    # 视图查询

    def get_book_info_view(self):

        query = "SELECT * FROM book_info_view"

        return self.db.execute_query(query)



    def get_borrow_info_view(self):

        query = "SELECT * FROM borrow_info_view"

        return self.db.execute_query(query)



    # 自定义函数调用

    def calculate_overdue_days(self, borrow_date, due_date, return_date):

        query = "SELECT calculate_overdue_days(%s, %s, %s) AS overdue_days"

        result = self.db.execute_query(query, (borrow_date, due_date, return_date))

        return result[0]['overdue_days'] if result else 0



    def calculate_fine(self, overdue_days):

        query = "SELECT calculate_fine(%s) AS fine_amount"

        result = self.db.execute_query(query, (str(overdue_days),))

        return result[0]['fine_amount'] if result else 0

