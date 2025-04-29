from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI
import os

# 从环境变量中读取 API key
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
else:
    print("api_key",api_key)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self,client=None,config=None):
        chroma_config = {
          "path": os.path.join(".", "golden_db"),  # 关键参数
          "client": "persistent",  # 必须为持久化模式
          "n_results": 1,  # 其他参数按需配置
        }
        ChromaDB_VectorStore.__init__(self, config=chroma_config)
        OpenAI_Chat.__init__(self,client=client, config=config)

vn = MyVanna(client=client,config={"model": "deepseek-chat","temperature":0.5})

#删除掉原有定义
# vn.remove_collection("documentation");
# vn.remove_collection("ddl");
# vn.remove_collection("sql");

print("Deep training completed.")

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run(host='0.0.0.0',port=8083,threaded=True,processes=1)
