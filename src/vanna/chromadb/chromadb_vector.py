import json
import logging
import os
from typing import List
from logging.handlers import RotatingFileHandler

import chromadb
import pandas as pd
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..base import VannaBase
from ..utils import deterministic_uuid

# 配置日志
logger = logging.getLogger('vanna.vector_search')
logger.setLevel(logging.INFO)

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 创建文件处理器
file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, 'vector_search.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

default_ef = embedding_functions.DefaultEmbeddingFunction()


class ChromaDB_VectorStore(VannaBase):
    def __init__(self, config=None):
        VannaBase.__init__(self, config=config)
        if config is None:
            config = {}

        path = config.get("path", ".")
        self.embedding_function = config.get("embedding_function", default_ef)
        curr_client = config.get("client", "persistent")
        collection_metadata = config.get("collection_metadata", None)
        self.n_results_sql = config.get("n_results_sql", config.get("n_results", 10))
        self.n_results_documentation = config.get("n_results_documentation", config.get("n_results", 10))
        self.n_results_ddl = config.get("n_results_ddl", config.get("n_results", 10))

        if curr_client == "persistent":
            self.chroma_client = chromadb.PersistentClient(
                path=path, settings=Settings(anonymized_telemetry=False)
            )
        elif curr_client == "in-memory":
            self.chroma_client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        elif isinstance(curr_client, chromadb.api.client.Client):
            # allow providing client directly
            self.chroma_client = curr_client
        else:
            raise ValueError(f"Unsupported client was set in config: {curr_client}")

        self.documentation_collection = self.chroma_client.get_or_create_collection(
            name="documentation",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )
        self.ddl_collection = self.chroma_client.get_or_create_collection(
            name="ddl",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )
        self.sql_collection = self.chroma_client.get_or_create_collection(
            name="sql",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )

    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        question_sql_json = json.dumps(
            {
                "question": question,
                "sql": sql,
            },
            ensure_ascii=False,
        )
        id = deterministic_uuid(question_sql_json) + "-sql"
        self.sql_collection.add(
            documents=question_sql_json,
            embeddings=self.generate_embedding(question_sql_json),
            ids=id,
        )

        return id

    def add_ddl(self, ddl: str, **kwargs) -> str:
        id = deterministic_uuid(ddl) + "-ddl"
        self.ddl_collection.add(
            documents=ddl,
            embeddings=self.generate_embedding(ddl),
            ids=id,
        )
        return id

    def add_documentation(self, documentation: str, **kwargs) -> str:
        id = deterministic_uuid(documentation) + "-doc"
        self.documentation_collection.add(
            documents=documentation,
            embeddings=self.generate_embedding(documentation),
            ids=id,
        )
        return id

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        sql_data = self.sql_collection.get()

        df = pd.DataFrame()

        if sql_data is not None:
            # Extract the documents and ids
            documents = [json.loads(doc) for doc in sql_data["documents"]]
            ids = sql_data["ids"]

            # Create a DataFrame
            df_sql = pd.DataFrame(
                {
                    "id": ids,
                    "question": [doc["question"] for doc in documents],
                    "content": [doc["sql"] for doc in documents],
                }
            )

            df_sql["training_data_type"] = "sql"

            df = pd.concat([df, df_sql])

        ddl_data = self.ddl_collection.get()

        if ddl_data is not None:
            # Extract the documents and ids
            documents = [doc for doc in ddl_data["documents"]]
            ids = ddl_data["ids"]

            # Create a DataFrame
            df_ddl = pd.DataFrame(
                {
                    "id": ids,
                    "question": [None for doc in documents],
                    "content": [doc for doc in documents],
                }
            )

            df_ddl["training_data_type"] = "ddl"

            df = pd.concat([df, df_ddl])

        doc_data = self.documentation_collection.get()

        if doc_data is not None:
            # Extract the documents and ids
            documents = [doc for doc in doc_data["documents"]]
            ids = doc_data["ids"]

            # Create a DataFrame
            df_doc = pd.DataFrame(
                {
                    "id": ids,
                    "question": [None for doc in documents],
                    "content": [doc for doc in documents],
                }
            )

            df_doc["training_data_type"] = "documentation"

            df = pd.concat([df, df_doc])

        return df

    def remove_training_data(self, id: str, **kwargs) -> bool:
        if id.endswith("-sql"):
            self.sql_collection.delete(ids=id)
            return True
        elif id.endswith("-ddl"):
            self.ddl_collection.delete(ids=id)
            return True
        elif id.endswith("-doc"):
            self.documentation_collection.delete(ids=id)
            return True
        else:
            return False

    def remove_collection(self, collection_name: str) -> bool:
        """
        This function can reset the collection to empty state.

        Args:
            collection_name (str): sql or ddl or documentation

        Returns:
            bool: True if collection is deleted, False otherwise
        """
        if collection_name == "sql":
            self.chroma_client.delete_collection(name="sql")
            self.sql_collection = self.chroma_client.get_or_create_collection(
                name="sql", embedding_function=self.embedding_function
            )
            return True
        elif collection_name == "ddl":
            self.chroma_client.delete_collection(name="ddl")
            self.ddl_collection = self.chroma_client.get_or_create_collection(
                name="ddl", embedding_function=self.embedding_function
            )
            return True
        elif collection_name == "documentation":
            self.chroma_client.delete_collection(name="documentation")
            self.documentation_collection = self.chroma_client.get_or_create_collection(
                name="documentation", embedding_function=self.embedding_function
            )
            return True
        else:
            return False

    @staticmethod
    def _extract_documents(query_results) -> list:
        """
        Static method to extract the documents from the results of a query.

        Args:
            query_results (pd.DataFrame): The dataframe to use.

        Returns:
            List[dict]: The extracted documents with similarity scores, or an empty list if an error occurred.
        """
        if query_results is None:
            return []

        if "documents" in query_results:
            documents = query_results["documents"]
            distances = query_results.get("distances", [])
            
            if len(documents) == 1 and isinstance(documents[0], list):
                try:
                    # 将文档和相似度分数组合在一起
                    results = []
                    for doc, distance in zip(documents[0], distances[0]):
                        try:
                            parsed_doc = json.loads(doc)
                            parsed_doc["similarity_score"] = 1 - distance  # 将距离转换为相似度分数
                            results.append(parsed_doc)
                        except json.JSONDecodeError:
                            results.append({
                                "content": doc,
                                "similarity_score": 1 - distance
                            })
                    return results
                except Exception as e:
                    return [{
                        "content": documents[0],
                        "similarity_score": 1 - distances[0][0] if distances else None
                    }]

            return documents

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        results = self.sql_collection.query(
            query_texts=[question],
            n_results=self.n_results_sql,
        )
        extracted_results = ChromaDB_VectorStore._extract_documents(results)
        
        # 记录日志
        for result in extracted_results:
            logger.info(f"SQL检索 - 问题: {question}, 相似度: {result.get('similarity_score', 'N/A')}, 内容: {result.get('sql', 'N/A')}")
        
        return extracted_results

    def get_related_ddl(self, question: str, **kwargs) -> list:
        results = self.ddl_collection.query(
            query_texts=[question],
            n_results=self.n_results_ddl,
        )
        extracted_results = ChromaDB_VectorStore._extract_documents(results)
        
        # 记录日志
        for result in extracted_results:
            logger.info(f"DDL检索 - 问题: {question}, 相似度: {result.get('similarity_score', 'N/A')}, 内容: {result.get('content', 'N/A')}")
        
        return [result.get('content', '') for result in extracted_results]

    def get_related_documentation(self, question: str, **kwargs) -> list:
        results = self.documentation_collection.query(
            query_texts=[question],
            n_results=self.n_results_documentation,
        )
        extracted_results = ChromaDB_VectorStore._extract_documents(results)
        
        # 记录日志
        for result in extracted_results:
            logger.info(f"文档检索 - 问题: {question}, 相似度: {result.get('similarity_score', 'N/A')}, 内容: {result.get('content', 'N/A')}")
        
        return [result.get('content', '') for result in extracted_results]
