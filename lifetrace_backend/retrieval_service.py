import logging
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径，以便直接运行此文件
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import DatabaseManager
from lifetrace_backend.query_parser import QueryParser, QueryConditions
from lifetrace_backend.models import Screenshot, OCRResult
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)

class RetrievalService:
    """检索服务，用于从数据库中检索相关的截图和OCR数据"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化检索服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.query_parser = QueryParser()
        logger.info("检索服务初始化完成")
    
    def search_by_conditions(self, conditions: QueryConditions, limit: int = 50) -> List[Dict[str, Any]]:
        """
        根据查询条件检索数据
        
        Args:
            conditions: 查询条件
            limit: 返回结果的最大数量
            
        Returns:
            检索到的数据列表
        """
        try:
            logger.info(f"执行数据库查询 - 条件: {conditions}, 限制: {limit}")
            
            with self.db_manager.get_session() as session:
                # 构建基础查询
                query = session.query(Screenshot).join(OCRResult, Screenshot.id == OCRResult.screenshot_id)
                
                # 添加时间范围过滤
                if conditions.start_date:
                    query = query.filter(Screenshot.created_at >= conditions.start_date)
                if conditions.end_date:
                    query = query.filter(Screenshot.created_at <= conditions.end_date)
                
                # 添加应用名称过滤
                if conditions.app_names:
                    app_filters = [Screenshot.app_name.ilike(f"%{app}%") for app in conditions.app_names]
                    query = query.filter(or_(*app_filters))
                
                # 添加关键词过滤
                if conditions.keywords:
                    keyword_filters = []
                    for keyword in conditions.keywords:
                        keyword_filters.append(OCRResult.text_content.ilike(f"%{keyword}%"))
                    
                    if len(keyword_filters) > 1:
                        # 多个关键词使用OR连接
                        query = query.filter(or_(*keyword_filters))
                    else:
                        query = query.filter(keyword_filters[0])
                
                # 按时间倒序排列
                query = query.order_by(Screenshot.created_at.desc())
                
                # 限制结果数量 - 优先使用QueryConditions中的limit
                effective_limit = conditions.limit if conditions.limit else limit
                results = query.limit(effective_limit).all()
                
                # 转换为字典格式
                data_list = []
                for screenshot in results:
                    # 获取对应的OCR结果
                    ocr_results = session.query(OCRResult).filter(
                        OCRResult.screenshot_id == screenshot.id
                    ).all()
                    
                    ocr_text = " ".join([ocr.text_content for ocr in ocr_results if ocr.text_content])
                    
                    data_item = {
                        "screenshot_id": screenshot.id,
                        "timestamp": screenshot.created_at.isoformat() if screenshot.created_at else None,
                        "app_name": screenshot.app_name,
                        "window_title": screenshot.window_title,
                        "file_path": screenshot.file_path,
                        "ocr_text": ocr_text,
                        "ocr_count": len(ocr_results),
                        "relevance_score": self._calculate_relevance(screenshot, ocr_text, conditions)
                    }
                    data_list.append(data_item)
                
                # 按相关性得分排序
                data_list.sort(key=lambda x: x["timestamp"], reverse=True)
                
                # 记录查询结果
                print(f"查询结果: 找到 {len(data_list)} 条记录")
                if data_list:
                    print(f"结果预览:")
                    for i, item in enumerate(data_list[:3]):
                        print(f"  {i+1}. ID:{item['screenshot_id']}, 应用:{item['app_name']}, 时间:{item['timestamp']}, 相关性:{item['relevance_score']:.2f}")
                    for i, item in enumerate(data_list[-3:]):
                        print(f"  {i+1}. ID:{item['screenshot_id']}, 应用:{item['app_name']}, 时间:{item['timestamp']}, 相关性:{item['relevance_score']:.2f}")
                print(f"=== 查询完成 ===")
                
                logger.info(f"检索完成，找到 {len(data_list)} 条记录")
                return data_list
                
        except Exception as e:
            logger.error(f"数据检索失败: {e}")
            return []
    
    def search_by_query(self, user_query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        根据用户查询检索数据
        
        Args:
            user_query: 用户的自然语言查询
            limit: 返回结果的最大数量
            
        Returns:
            检索到的数据列表
        """
        # 解析查询
        conditions = self.query_parser.parse_query(user_query)
        logger.info(f"查询解析结果: {conditions}")
        
        # 执行检索
        return self.search_by_conditions(conditions, limit)
    
    def search_recent(self, hours: int = 24, app_name: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        检索最近的记录
        
        Args:
            hours: 最近多少小时的记录
            app_name: 可选的应用名称过滤
            limit: 返回结果的最大数量
            
        Returns:
            检索到的数据列表
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        conditions = QueryConditions(
            start_date=start_time,
            end_date=end_time,
            app_names=[app_name] if app_name else None
        )
        
        return self.search_by_conditions(conditions, limit)
    
    def search_by_app(self, app_name: str, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        按应用名称检索记录
        
        Args:
            app_name: 应用名称
            days: 检索最近多少天的记录
            limit: 返回结果的最大数量
            
        Returns:
            检索到的数据列表
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        conditions = QueryConditions(
            start_date=start_time,
            end_date=end_time,
            app_names=[app_name] if app_name else None
        )
        
        return self.search_by_conditions(conditions, limit)
    
    def search_by_keywords(self, keywords: List[str], days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """
        按关键词检索记录
        
        Args:
            keywords: 关键词列表
            days: 检索最近多少天的记录
            limit: 返回结果的最大数量
            
        Returns:
            检索到的数据列表
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        conditions = QueryConditions(
            start_date=start_time,
            end_date=end_time,
            keywords=keywords
        )
        
        return self.search_by_conditions(conditions, limit)
    
    def get_statistics(self, conditions: QueryConditions = None) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            conditions: 可选的查询条件
            
        Returns:
            统计信息字典
        """
        try:
            # 记录统计查询条件
            print(f"\n=== 数据库查询 - get_statistics ===")
            print(f"统计查询条件: {conditions}")
            logger.info(f"执行统计查询 - 条件: {conditions}")
            
            with self.db_manager.get_session() as session:
                # 基础查询
                query = session.query(Screenshot)
                
                # 应用条件过滤
                if conditions:
                    if conditions.start_date:
                        query = query.filter(Screenshot.created_at >= conditions.start_date)
                    if conditions.end_date:
                        query = query.filter(Screenshot.created_at <= conditions.end_date)
                    if conditions.app_names:
                        # 支持多个应用名称过滤
                        app_filters = [Screenshot.app_name.ilike(f"%{app}%") for app in conditions.app_names]
                        query = query.filter(or_(*app_filters))
                
                # 总记录数
                total_count = query.count()
                
                # 按应用分组统计
                app_stats = session.query(
                    Screenshot.app_name,
                    func.count(Screenshot.id).label('count')
                ).group_by(Screenshot.app_name)
                
                if conditions:
                    if conditions.start_date:
                        app_stats = app_stats.filter(Screenshot.created_at >= conditions.start_date)
                    if conditions.end_date:
                        app_stats = app_stats.filter(Screenshot.created_at <= conditions.end_date)
                
                app_stats = app_stats.all()
                
                # 时间范围
                time_range = query.with_entities(
                    func.min(Screenshot.created_at).label('earliest'),
                    func.max(Screenshot.created_at).label('latest')
                ).first()
                
                stats = {
                    "total_screenshots": total_count,
                    "app_distribution": {app: count for app, count in app_stats},
                    "time_range": {
                        "earliest": time_range.earliest.isoformat() if time_range.earliest else None,
                        "latest": time_range.latest.isoformat() if time_range.latest else None
                    },
                    "query_conditions": {
                        "start_date": conditions.start_date.isoformat() if conditions and conditions.start_date else None,
                        "end_date": conditions.end_date.isoformat() if conditions and conditions.end_date else None,
                        "app_names": conditions.app_names if conditions else None,
                        "keywords": conditions.keywords if conditions else []
                    }
                }
                
                # 记录统计结果
                print(f"统计结果:")
                print(f"  总截图数: {total_count}")
                print(f"  应用分布: {dict(list(stats['app_distribution'].items())[:5])}{'...' if len(stats['app_distribution']) > 5 else ''}")
                print(f"  时间范围: {stats['time_range']['earliest']} 到 {stats['time_range']['latest']}")
                print(f"=== 统计查询完成 ===")
                
                logger.info(f"统计信息获取完成: {total_count} 条记录")
                return stats
                
        except Exception as e:
            logger.error(f"统计信息获取失败: {e}")
            return {
                "total_screenshots": 0,
                "app_distribution": {},
                "time_range": {"earliest": None, "latest": None},
                "query_conditions": {}
            }
    
    def _calculate_relevance(self, screenshot: Screenshot, ocr_text: str, conditions: QueryConditions) -> float:
        """
        计算相关性得分
        
        Args:
            screenshot: 截图对象
            ocr_text: OCR文本
            conditions: 查询条件
            
        Returns:
            相关性得分 (0.0 - 1.0)
        """
        score = 0.0
        
        # 应用名称匹配加分
        if conditions.app_names and screenshot.app_name:
            if any(app.lower() in screenshot.app_name.lower() for app in conditions.app_names):
                score += 0.3
        
        # 关键词匹配加分
        if conditions.keywords and ocr_text:
            text_lower = ocr_text.lower()
            keyword_matches = 0
            for keyword in conditions.keywords:
                if keyword.lower() in text_lower:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                score += 0.5 * (keyword_matches / len(conditions.keywords))
        
        # 时间新近性加分
        if screenshot.created_at:
            now = datetime.now()
            time_diff = now - screenshot.created_at
            if time_diff.days < 1:
                score += 0.2
            elif time_diff.days < 7:
                score += 0.1
        
        return min(score, 1.0)