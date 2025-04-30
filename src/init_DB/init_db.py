import mysql.connector
from mysql.connector import Error
import os
import time

def clear_database(cursor):
    try:
        print("开始清空数据库...")
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"找到 {len(tables)} 个表需要清理")
        
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        print("已禁用外键检查")
        
        # 清空每个表
        for i, table in enumerate(tables, 1):
            try:
                table_name = table[0]
                print(f"正在删除表 {i}/{len(tables)}: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"成功删除表: {table_name}")
                time.sleep(0.1)  # 添加短暂延迟，避免操作过快
            except Error as e:
                print(f"删除表 {table_name} 时出错: {str(e)}")
                continue
        
        # 重新启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("已重新启用外键检查")
        print("数据库清空完成")
        
    except Error as e:
        print(f"清空数据库时出错: {str(e)}")
        raise  # 重新抛出异常，让上层函数处理

def init_database():
    connection = None
    cursor = None
    try:
        print("开始初始化数据库...")
        # 从环境变量获取数据库连接信息
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': 'GAODA'
        }

        print("正在连接数据库...")
        # 建立数据库连接
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            
            # 创建游标
            cursor = connection.cursor()
            
            # 清空数据库
            clear_database(cursor)
            
            # 获取脚本所在目录的绝对路径
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sql_file_path = os.path.join(script_dir, 'ect.sql')
            print(f"准备执行SQL文件: {sql_file_path}")
            
            # 读取并执行SQL文件
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_commands = file.read().split(';')
                print(f"找到 {len(sql_commands)} 条SQL命令需要执行")
                
                for i, command in enumerate(sql_commands, 1):
                    if command.strip():
                        try:
                            print(f"正在执行第 {i}/{len(sql_commands)} 条SQL命令...")
                            cursor.execute(command)
                            print(f"成功执行SQL命令: {command[:50]}...")
                        except Error as e:
                            print(f"执行SQL命令时出错: {str(e)}")
                            print(f"出错的SQL命令: {command}")
                            continue
                
            # 提交事务
            connection.commit()
            print("所有SQL命令执行完成")
            
    except Error as e:
        print(f"数据库操作出错: {str(e)}")
        if connection:
            connection.rollback()
            print("已回滚事务")
        
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
            print("游标已关闭")
        if connection and connection.is_connected():
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    init_database() 