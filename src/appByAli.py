from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI
import os

# 从环境变量中读取 API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
else:
    print("api_key",api_key)

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
