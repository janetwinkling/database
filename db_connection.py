import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, connection_string):
        params = {}
        for param in connection_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip().lower()] = value.strip()

        self.host = params.get('host', 'localhost')
        self.user = params.get('user', 'root')
        self.password = params.get('password', '')
        self.database = params.get('database', '')
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False  # 自动进入事务模式
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"连接数据库时出错: {e}")
            return False

    def disconnect(self):
      try:
        if self.cursor:
            try:
                self.cursor.close()
            except ReferenceError:
                pass  # 忽略已被释放的引用

        if self.connection:
            try:
                self.connection.close()
            except ReferenceError:
                pass
      except Exception as e:
        print(f"断开连接时发生异常: {e}")

    def execute_query(self, query, params=None):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params or ())
            
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.rowcount
        except Error as e:
            print(f"执行查询时出错: {e}")
            self.connection.rollback()
            return None

    def execute_procedure(self, procedure_name, params=None):
     try:
        if not self.connection or not self.connection.is_connected():
            self.connect()

        if params is None:
            params = []

        processed_params = []
        for param in params:
            if isinstance(param, str) and param.startswith('@'):
                var_name = param[1:]
                self.cursor.execute(f"SET @{var_name} = NULL")
                processed_params.append(f"@{var_name}")
            else:
                processed_params.append(param)

        param_placeholders = ', '.join([
            '%s' if not isinstance(p, str) or not p.startswith('@') else p
            for p in processed_params
        ])
        call_query = f"CALL {procedure_name}({param_placeholders})"

        # 执行 CALL 语句，去除掉 @变量参数
        call_params = [
            p for p in processed_params
            if not isinstance(p, str) or not p.startswith('@')
        ]
        self.cursor.execute(call_query, call_params)

        results = []
        try:
            result = self.cursor.fetchall()
            if result:
                results.append(result)
        except:
            pass

        while self.cursor.nextset():
            try:
                result = self.cursor.fetchall()
                if result:
                    results.append(result)
            except:
                continue

        # 获取输出参数（@变量）
        output_params = {}
        for param in params:
            if isinstance(param, str) and param.startswith('@'):
                var_name = param[1:]
                self.cursor.execute(f"SELECT @{var_name} AS value")
                output_value = self.cursor.fetchone()
                if output_value:
                    output_params[var_name] = output_value['value']

        if output_params:
            results.append([output_params])

        # ✅ 提交事务，防止锁表
        self.connection.commit()

        return results

     except Error as e:
        print(f"执行存储过程时出错: {e}")
        # ✅ 出错回滚事务
        if self.connection:
            self.connection.rollback()
        return None


    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()