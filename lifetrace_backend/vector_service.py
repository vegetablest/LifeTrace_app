"""向量数据库服务模块

提供 OCR 结果的向量化存储和语义搜索服务。
与现有的 SQLite 数据库并行工作。
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from .vector_db import VectorDatabase, create_vector_db
from .storage import DatabaseManager
from .models import OCRResult, Screenshot
from .config import config


class VectorService:
    """向量数据库服务
    
    负责将 OCR 结果存储到向量数据库，并提供语义搜索功能。
    """
    
    def __init__(self, config, db_manager: DatabaseManager):
        """初始化向量服务
        
        Args:
            config: 配置对象
            db_manager: 数据库管理器
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # 初始化向量数据库
        self.vector_db = create_vector_db(config)
        if self.vector_db is None:
            self.logger.warning("Vector database not available")
            self.enabled = False
        else:
            self.enabled = True
            self.logger.info("Vector service initialized successfully")
    
    def is_enabled(self) -> bool:
        """检查向量服务是否可用"""
        return self.enabled and self.vector_db is not None
    
    def add_ocr_result(self, ocr_result: OCRResult, screenshot: Optional[Screenshot] = None) -> bool:
        """添加 OCR 结果到向量数据库
        
        Args:
            ocr_result: OCR 结果对象
            screenshot: 关联的截图对象（可选）
            
        Returns:
            是否添加成功
        """
        if not self.is_enabled():
            return False
        
        if not ocr_result.text_content or not ocr_result.text_content.strip():
            self.logger.debug(f"Skipping empty OCR result {ocr_result.id}")
            return False
        
        try:
            # 构建文档 ID
            doc_id = f"ocr_{ocr_result.id}"
            
            # 构建元数据
            metadata = {
                "ocr_result_id": ocr_result.id,
                "screenshot_id": ocr_result.screenshot_id,
                "confidence": ocr_result.confidence,
                "language": ocr_result.language or "unknown",
                "processing_time": ocr_result.processing_time,
                "created_at": ocr_result.created_at.isoformat() if ocr_result.created_at else None,
                "text_length": len(ocr_result.text_content)
            }
            
            # 添加截图相关信息
            if screenshot:
                metadata.update({
                    "screenshot_path": screenshot.file_path,
                    "screenshot_timestamp": screenshot.created_at.isoformat() if screenshot.created_at else None,
                    "application": screenshot.app_name,
                    "window_title": screenshot.window_title,
                    "width": screenshot.width,
                    "height": screenshot.height
                })
            
            # 添加到向量数据库
            success = self.vector_db.add_document(
                doc_id=doc_id,
                text=ocr_result.text_content,
                metadata=metadata
            )
            
            if success:
                self.logger.debug(f"Added OCR result {ocr_result.id} to vector database")
            else:
                self.logger.warning(f"Failed to add OCR result {ocr_result.id} to vector database")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error adding OCR result {ocr_result.id} to vector database: {e}")
            return False
    
    def update_ocr_result(self, ocr_result: OCRResult, screenshot: Optional[Screenshot] = None) -> bool:
        """更新向量数据库中的 OCR 结果
        
        Args:
            ocr_result: OCR 结果对象
            screenshot: 关联的截图对象（可选）
            
        Returns:
            是否更新成功
        """
        if not self.is_enabled():
            return False
        
        try:
            doc_id = f"ocr_{ocr_result.id}"
            
            # 构建元数据
            metadata = {
                "ocr_result_id": ocr_result.id,
                "screenshot_id": ocr_result.screenshot_id,
                "confidence": ocr_result.confidence,
                "language": ocr_result.language or "unknown",
                "processing_time": ocr_result.processing_time,
                "created_at": ocr_result.created_at.isoformat() if ocr_result.created_at else None,
                "updated_at": datetime.now().isoformat(),
                "text_length": len(ocr_result.text_content or "")
            }
            
            if screenshot:
                metadata.update({
                    "screenshot_path": screenshot.file_path,
                    "screenshot_timestamp": screenshot.created_at.isoformat() if screenshot.created_at else None,
                    "application": screenshot.app_name,
                    "window_title": screenshot.window_title,
                    "width": screenshot.width,
                    "height": screenshot.height
                })
            
            success = self.vector_db.update_document(
                doc_id=doc_id,
                text=ocr_result.text_content or "",
                metadata=metadata
            )
            
            if success:
                self.logger.debug(f"Updated OCR result {ocr_result.id} in vector database")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating OCR result {ocr_result.id} in vector database: {e}")
            return False
    
    def delete_ocr_result(self, ocr_result_id: int) -> bool:
        """从向量数据库中删除 OCR 结果
        
        Args:
            ocr_result_id: OCR 结果 ID
            
        Returns:
            是否删除成功
        """
        if not self.is_enabled():
            return False
        
        try:
            doc_id = f"ocr_{ocr_result_id}"
            success = self.vector_db.delete_document(doc_id)
            
            if success:
                self.logger.debug(f"Deleted OCR result {ocr_result_id} from vector database")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting OCR result {ocr_result_id} from vector database: {e}")
            return False
    
    def semantic_search(self, 
                       query: str, 
                       top_k: int = 10,
                       use_rerank: bool = True,
                       retrieve_k: Optional[int] = None,
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """语义搜索 OCR 结果
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            use_rerank: 是否使用重排序
            retrieve_k: 初始检索数量（用于重排序）
            filters: 元数据过滤条件
            
        Returns:
            搜索结果列表
        """
        if not self.is_enabled():
            return []
        
        if not query or not query.strip():
            return []
        
        try:
            if use_rerank:
                # 使用重排序搜索
                if retrieve_k is None:
                    retrieve_k = min(top_k * 3, 50)  # 默认检索 3 倍数量用于重排序
                
                results = self.vector_db.search_and_rerank(
                    query=query,
                    retrieve_k=retrieve_k,
                    rerank_k=top_k,
                    where=filters
                )
            else:
                # 直接搜索
                results = self.vector_db.search(
                    query=query,
                    top_k=top_k,
                    where=filters
                )
            
            # 增强结果信息
            enhanced_results = []
            for result in results:
                enhanced_result = result.copy()
                
                # 统一score字段：优先使用rerank_score，其次使用distance转换为相似度
                if 'rerank_score' in result:
                    enhanced_result['score'] = float(result['rerank_score'])
                elif 'distance' in result and result['distance'] is not None:
                    # 将距离转换为相似度分数 (距离越小，相似度越高)
                    distance = float(result['distance'])
                    # 使用简单的转换公式：score = max(0, 1 - distance)
                    enhanced_result['score'] = max(0.0, 1.0 - distance)
                else:
                    enhanced_result['score'] = 0.0
                
                # 提取 OCR 结果 ID
                if 'metadata' in result and 'ocr_result_id' in result['metadata']:
                    ocr_result_id = result['metadata']['ocr_result_id']
                    
                    # 从数据库获取完整的 OCR 结果信息
                    try:
                        with self.db_manager.get_session() as session:
                            ocr_result = session.query(OCRResult).filter(
                                OCRResult.id == ocr_result_id
                            ).first()
                            
                            if ocr_result:
                                enhanced_result['ocr_result'] = {
                                    'id': ocr_result.id,
                                    'screenshot_id': ocr_result.screenshot_id,
                                    'text_content': ocr_result.text_content,
                                    'confidence': ocr_result.confidence,
                                    'language': ocr_result.language,
                                    'processing_time': ocr_result.processing_time,
                                    'created_at': ocr_result.created_at.isoformat() if ocr_result.created_at else None
                                }
                                
                                # 确保metadata中有created_at字段
                                if 'metadata' not in enhanced_result:
                                    enhanced_result['metadata'] = {}
                                if 'created_at' not in enhanced_result['metadata'] and ocr_result.created_at:
                                    enhanced_result['metadata']['created_at'] = ocr_result.created_at.isoformat()
                                
                                # 获取关联的截图信息
                                screenshot = session.query(Screenshot).filter(
                                    Screenshot.id == ocr_result.screenshot_id
                                ).first()
                                
                                if screenshot:
                                    enhanced_result['screenshot'] = {
                                        'id': screenshot.id,
                                        'file_path': screenshot.file_path,
                                        'timestamp': screenshot.created_at.isoformat() if screenshot.created_at else None,
                                        'application': screenshot.app_name,
                                        'window_title': screenshot.window_title,
                                        'width': screenshot.width,
                                        'height': screenshot.height
                                    }
                    except Exception as e:
                        self.logger.warning(f"Failed to enhance result for OCR {ocr_result_id}: {e}")
                
                enhanced_results.append(enhanced_result)
            
            self.logger.info(f"Semantic search for '{query}' returned {len(enhanced_results)} results")
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []
    
    def sync_from_database(self, limit: Optional[int] = None, force_reset: bool = False) -> int:
        """从 SQLite 数据库同步 OCR 结果到向量数据库
        
        Args:
            limit: 同步的最大记录数，None 表示同步全部
            force_reset: 是否先重置向量数据库
            
        Returns:
            同步的记录数
        """
        if not self.is_enabled():
            return 0
        
        try:
            with self.db_manager.get_session() as session:
                # 检查SQLite数据库中的OCR结果数量
                total_ocr_count = session.query(OCRResult).count()
                self.logger.info(f"SQLite database has {total_ocr_count} OCR results")
                
                # 获取向量数据库中的文档数量
                vector_stats = self.vector_db.get_collection_stats()
                vector_doc_count = vector_stats.get('document_count', 0)
                self.logger.info(f"Vector database has {vector_doc_count} documents")
                
                # 如果SQLite为空但向量数据库不为空，或者强制重置，则清空向量数据库
                if (total_ocr_count == 0 and vector_doc_count > 0) or force_reset:
                    self.logger.info("Resetting vector database to match empty SQLite database")
                    self.reset()
                    if total_ocr_count == 0:
                        return 0  # SQLite为空，同步完成
                
                # 如果两个数据库都为空，无需同步
                if total_ocr_count == 0 and vector_doc_count == 0:
                    self.logger.info("Both databases are empty, no sync needed")
                    return 0
                
                synced_count = 0
                
                # 查询所有 OCR 结果
                query = session.query(OCRResult).join(Screenshot, OCRResult.screenshot_id == Screenshot.id)
                if limit:
                    query = query.limit(limit)
                
                ocr_results = query.all()
                
                # 如果需要完全同步，先重置向量数据库
                if not limit and len(ocr_results) != vector_doc_count:
                    self.logger.info(f"Document count mismatch (SQLite: {len(ocr_results)}, Vector: {vector_doc_count}), resetting vector database")
                    self.reset()
                
                for ocr_result in ocr_results:
                    # 通过 screenshot_id 获取对应的 Screenshot 对象
                    screenshot = session.query(Screenshot).filter(Screenshot.id == ocr_result.screenshot_id).first()
                    if screenshot is None:
                        self.logger.warning(f"Screenshot not found for OCR result {ocr_result.id}")
                        continue
                    
                    if self.add_ocr_result(ocr_result, screenshot):
                        synced_count += 1
                    
                    if synced_count % 100 == 0:
                        self.logger.info(f"Synced {synced_count} OCR results to vector database")
            
            self.logger.info(f"Completed sync: {synced_count} OCR results added to vector database")
            return synced_count
            
        except Exception as e:
            self.logger.error(f"Error syncing from database: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取向量数据库统计信息
        
        Returns:
            统计信息字典
        """
        if not self.is_enabled():
            return {"enabled": False, "reason": "Vector database not available"}
        
        try:
            stats = self.vector_db.get_collection_stats()
            stats["enabled"] = True
            return stats
        except Exception as e:
            self.logger.error(f"Error getting vector database stats: {e}")
            return {"enabled": True, "error": str(e)}
    
    def reset(self) -> bool:
        """重置向量数据库
        
        Returns:
            是否重置成功
        """
        if not self.is_enabled():
            return False
        
        try:
            success = self.vector_db.reset_collection()
            if success:
                self.logger.info("Vector database reset successfully")
            return success
        except Exception as e:
            self.logger.error(f"Error resetting vector database: {e}")
            return False


def create_vector_service(config, db_manager: DatabaseManager) -> VectorService:
    """创建向量服务实例
    
    Args:
        config: 配置对象
        db_manager: 数据库管理器
        
    Returns:
        向量服务实例
    """
    return VectorService(config, db_manager)