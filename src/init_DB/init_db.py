import mysql.connector
from mysql.connector import Error
import os

def init_database():
    try:
        # 从环境变量获取数据库连接信息
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': 'GAODA'
        }

        # 建立数据库连接
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            
            # 创建游标
            cursor = connection.cursor()
            
            # 获取脚本所在目录的绝对路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sql_file_path = os.path.join(script_dir, 'ect.sql')
            
            # 读取并执行SQL文件
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_commands = file.read().split(';')
                
                for command in sql_commands:
                    if command.strip():
                        try:
                            cursor.execute(command)
                            print(f"成功执行SQL命令: {command[:50]}...")
                        except Error as e:
                            print(f"执行SQL命令时出错: {str(e)}")
                            print(f"出错的SQL命令: {command}")
                
            # 提交事务
            connection.commit()
            print("所有SQL命令执行完成")
            
    except Error as e:
        print(f"连接数据库时出错: {str(e)}")
        
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    init_database() 