import sys
import os
import logging

# 将当前目录添加到Python路径中，确保优先使用本地模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI

# 添加断言确保使用的是当前项目下的vanna模块
import vanna
assert os.path.dirname(vanna.__file__) == os.path.join(current_dir, "vanna"), "请确保使用的是当前项目下的vanna模块，而不是系统安装的vanna模块"

# 从环境变量中读取 API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self,client=None,config=None):
        chroma_config = {
          "path": os.path.join(".", "golden_db"),  # 关键参数
          "client": "persistent",  # 必须为持久化模式
          "n_results": 10,  # 其他参数按需配置
        }
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        OpenAI_Chat.__init__(self,client=client, config=config)
    
    # 实现抽象方法search_tables_metadata，满足抽象方法要求
    def search_tables_metadata(self, engine=None, catalog=None, schema=None, table_name=None, ddl=None, size=10, **kwargs):
        """
        搜索和检索数据库表的元数据信息
        
        当前实现仅返回空列表，满足抽象方法要求
        """
        # 简单实现，返回空列表
        return []

# 删除旧的数据库文件
import shutil
if os.path.exists("golden_db"):
    shutil.rmtree("golden_db")

# 创建新的实例，这会自动创建新的集合
vn = MyVanna(client=client,config={"model": "qwen-plus","temperature":0.5})

# 添加初始化日志
logger = logging.getLogger('vanna.vector_search')
logger.info("qwen-max + chorom 初始化完成")

# 检查MySQL密码是否设置
mysql_password = os.getenv("MYSQL_PASSWORD")
if not mysql_password:
    raise ValueError("请设置环境变量 MYSQL_PASSWORD 来配置MySQL数据库密码")

# 连接MySQL数据库
vn.connect_to_mysql(
    host="localhost",
    dbname="GAODA",
    user="root",
    password=mysql_password,
    port=3306
)

# 测试数据库连接是否成功
try:
    # 尝试执行一个简单的查询
    result = vn.run_sql("SELECT 1")
    assert result is not None, "数据库连接失败：无法执行查询"
    print("数据库连接测试成功！")
except Exception as e:
    raise AssertionError(f"数据库连接失败：{str(e)}")

vn.train(ddl="CREATE TABLE IF NOT EXISTS current_orders (order_id VARCHAR(50) PRIMARY KEY COMMENT '订单编号，主键', customer_id VARCHAR(50) NOT NULL COMMENT '客户编号', order_date DATETIME NOT NULL COMMENT '订单创建日期', order_status VARCHAR(20) NOT NULL COMMENT '订单当前状态：PENDING-待处理, PROCESSING-处理中, COMPLETED-已完成', total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额', payment_status VARCHAR(20) NOT NULL COMMENT '支付状态：UNPAID-未支付, PAID-已支付', shipping_address TEXT COMMENT '收货地址', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间') COMMENT='当前订单表，存储当前有效的订单信息，包含订单的基本信息，如订单状态、支付状态等'")
vn.train(ddl="CREATE TABLE IF NOT EXISTS historical_orders (order_id VARCHAR(50) PRIMARY KEY COMMENT '订单编号，主键', customer_id VARCHAR(50) NOT NULL COMMENT '客户编号', order_date DATETIME NOT NULL COMMENT '订单创建日期', completion_date DATETIME NOT NULL COMMENT '订单完成日期', final_status VARCHAR(20) NOT NULL COMMENT '订单最终状态：COMPLETED-已完成, CANCELLED-已取消', total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额', payment_method VARCHAR(20) COMMENT '支付方式：ALIPAY-支付宝, WECHAT-微信, BANK-银行转账', shipping_address TEXT COMMENT '收货地址', archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '订单归档时间') COMMENT='历史订单表，存储已完成的订单历史记录，包含订单的完成时间和最终状态'")
vn.train(ddl="CREATE TABLE IF NOT EXISTS order_items (item_id VARCHAR(50) PRIMARY KEY COMMENT '订单项编号，主键', order_id VARCHAR(50) NOT NULL COMMENT '所属订单编号，外键关联current_orders表', product_id VARCHAR(50) NOT NULL COMMENT '商品编号', product_name VARCHAR(100) NOT NULL COMMENT '商品名称', quantity INT NOT NULL COMMENT '商品数量', unit_price DECIMAL(10,2) NOT NULL COMMENT '商品单价', subtotal DECIMAL(10,2) NOT NULL COMMENT '商品小计金额', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间', FOREIGN KEY (order_id) REFERENCES current_orders(order_id)) COMMENT='订单明细表，存储订单的详细商品信息，包含商品数量、单价等详细信息'")
vn.train(ddl="CREATE TABLE IF NOT EXISTS order_status_changes (change_id VARCHAR(50) PRIMARY KEY COMMENT '状态变更记录编号，主键', order_id VARCHAR(50) NOT NULL COMMENT '订单编号，外键关联current_orders表', previous_status VARCHAR(20) NOT NULL COMMENT '变更前状态', new_status VARCHAR(20) NOT NULL COMMENT '变更后状态', change_reason TEXT COMMENT '状态变更原因', changed_by VARCHAR(50) NOT NULL COMMENT '变更操作人', changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间', FOREIGN KEY (order_id) REFERENCES current_orders(order_id)) COMMENT='订单状态变更表，记录订单状态的变化历史，包含状态变更的原因和时间'")
vn.train(ddl="CREATE TABLE IF NOT EXISTS order_payments (payment_id VARCHAR(50) PRIMARY KEY COMMENT '支付记录编号，主键', order_id VARCHAR(50) NOT NULL COMMENT '订单编号，外键关联current_orders表', payment_amount DECIMAL(10,2) NOT NULL COMMENT '支付金额', payment_method VARCHAR(20) NOT NULL COMMENT '支付方式：ALIPAY-支付宝, WECHAT-微信, BANK-银行转账', payment_status VARCHAR(20) NOT NULL COMMENT '支付状态：PENDING-处理中, SUCCESS-成功, FAILED-失败', transaction_id VARCHAR(100) COMMENT '第三方支付平台交易号', payment_date DATETIME NOT NULL COMMENT '支付时间', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间', FOREIGN KEY (order_id) REFERENCES current_orders(order_id)) COMMENT='订单支付记录表，记录订单的支付信息，包含支付方式、交易ID等支付相关信息'")

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run(host='0.0.0.0',port=8084,threaded=True,processes=1)
