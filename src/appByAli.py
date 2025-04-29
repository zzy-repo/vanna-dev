import sys
import os

# 将当前目录添加到Python路径中，确保优先使用本地模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI

# 从环境变量中读取 API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
else:
    print("api_key:",api_key)

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
        
        此方法用于：
        1. 根据提供的参数（引擎类型、目录、模式、表名或DDL语句）搜索表结构信息
        2. 返回与查询条件匹配的表元数据列表（表名、列名、数据类型、注释等）
        3. 在生成SQL查询时提供数据库结构的上下文信息
        4. 帮助用户了解数据库中的表结构
        
        当前实现仅返回空列表，满足抽象方法要求
        """
        # 简单实现，返回空列表
        return []

vn = MyVanna(client=client,config={"model": "qwen-plus","temperature":0.5})

#删除掉原有定义
vn.remove_collection("documentation");
vn.remove_collection("ddl");
vn.remove_collection("sql");

vn.train(ddl="CREATE TABLE BASIC_ORG (ORG_ABBREVIATE VARCHAR (60) COMMENT '机构简称', ORG_CODE VARCHAR (8) COMMENT '代码', ORG_NAME VARCHAR (160) COMMENT '机构名称', ORG_PHONE VARCHAR (20) COMMENT '机构电话', ORG_REMARK VARCHAR (250) COMMENT '备注', ORG_STATE SMALLINT COMMENT '状态(0-启用 1-停用)') COMMENT='机构信息，可用于查询机构基本信息'")
vn.train(ddl="CREATE TABLE SJJ250304001000 (ORG_CODE VARCHAR COMMENT '机构代码(机构)', DATAS_BALCORP VARCHAR COMMENT '客户代码(往来单位代码)', DATAS_BALCORPNAME VARCHAR COMMENT '客户名称(往来单位名称)', SCONTRACT_BILLCODE VARCHAR COMMENT '合同号码') COMMENT='客户应收款表，主要存放客户应收款信息,可用于查询客户应收款信息'")
vn.train(ddl="  CREATE TABLE SJJ250306001000 (WAREHOUSE_CODE VARCHAR COMMENT '仓库代码(仓库编码)', PNTREE_NAME VARCHAR COMMENT '产品类别(产品分类,产品大类)', PRODUCTAREA_NAME VARCHAR COMMENT '产地(钢厂或生产地)', PARTSNAME_NAME VARCHAR COMMENT '品名(产品名称)', GOODS_MATERIAL VARCHAR COMMENT '规格(产品规格)', GOODS_NUM BIGINT COMMENT '产品数量(数量)', GOODS_WEIGHT DECIMAL (18, 6) COMMENT '产品重量(重量)') COMMENT='实物库存信息表，存放各产品的库存信息'");
#

print("Ali training completed.")

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run(host='0.0.0.0',port=8084,threaded=True,processes=1)
