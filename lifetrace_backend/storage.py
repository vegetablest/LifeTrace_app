import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from pathlib import Path

# 添加项目根目录到Python路径，以便直接运行此文件
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from lifetrace_backend.config import config
from lifetrace_backend.models import Base, Screenshot, OCRResult, SearchIndex, ProcessingQueue, Event, AppUsageLog
from lifetrace_backend.utils import ensure_dir, get_file_hash


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or f"sqlite:///{config.database_path}"
        self.engine = None
        self.SessionLocal = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            if self.database_url.startswith('sqlite:///'):
                db_path = self.database_url.replace('sqlite:///', '')
                ensure_dir(os.path.dirname(db_path))
            
            # 创建引擎
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # 创建表
            Base.metadata.create_all(bind=self.engine)
            
            logging.info(f"数据库初始化完成: {self.database_url}")

            # 轻量级迁移：为已存在的 screenshots 表添加 event_id 列
            try:
                if self.database_url.startswith('sqlite:///'):
                    with self.engine.connect() as conn:
                        cols = [row[1] for row in conn.execute(text("PRAGMA table_info('screenshots')")).fetchall()]
                        if 'event_id' not in cols:
                            conn.execute(text("ALTER TABLE screenshots ADD COLUMN event_id INTEGER"))
                            logging.info("已为 screenshots 表添加 event_id 列")
            except Exception as me:
                logging.warning(f"检查/添加 screenshots.event_id 列失败: {me}")

            # 性能优化：添加关键索引
            self._create_performance_indexes()
            
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            raise
    
    def _create_performance_indexes(self):
        """创建性能优化索引"""
        try:
            if self.database_url.startswith('sqlite:///'):
                with self.engine.connect() as conn:
                    # 获取现有索引列表
                    existing_indexes = [row[1] for row in conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='index'")).fetchall()]
                    
                    # 定义需要创建的索引
                    indexes_to_create = [
                        ("idx_ocr_results_screenshot_id", "CREATE INDEX IF NOT EXISTS idx_ocr_results_screenshot_id ON ocr_results(screenshot_id)"),
                        ("idx_screenshots_created_at", "CREATE INDEX IF NOT EXISTS idx_screenshots_created_at ON screenshots(created_at)"),
                        ("idx_screenshots_app_name", "CREATE INDEX IF NOT EXISTS idx_screenshots_app_name ON screenshots(app_name)"),
                        ("idx_screenshots_event_id", "CREATE INDEX IF NOT EXISTS idx_screenshots_event_id ON screenshots(event_id)"),
                        ("idx_processing_queue_status", "CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON processing_queue(status)"),
                        ("idx_processing_queue_task_type", "CREATE INDEX IF NOT EXISTS idx_processing_queue_task_type ON processing_queue(task_type)")
                    ]
                    
                    # 创建索引
                    for index_name, create_sql in indexes_to_create:
                        if index_name not in existing_indexes:
                            conn.execute(text(create_sql))
                            logging.info(f"已创建性能索引: {index_name}")
                    
                    conn.commit()
                    logging.info("性能索引创建完成")
                    
        except Exception as e:
            logging.warning(f"创建性能索引失败: {e}")
            
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """获取数据库会话上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def add_screenshot(self, file_path: str, file_hash: str, width: int, height: int, 
                     screen_id: int = 0, app_name: str = None, window_title: str = None, event_id: Optional[int] = None) -> Optional[int]:
        """添加截图记录"""
        try:
            with self.get_session() as session:
                # 首先检查是否已存在相同路径的截图
                existing_path = session.query(Screenshot).filter_by(file_path=file_path).first()
                if existing_path:
                    logging.debug(f"跳过重复路径截图: {file_path}")
                    return existing_path.id
                
                # 检查是否已存在相同哈希的截图
                existing_hash = session.query(Screenshot).filter_by(file_hash=file_hash).first()
                if existing_hash and config.get('storage.deduplicate', True):
                    logging.debug(f"跳过重复哈希截图: {file_path}")
                    return existing_hash.id
                
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                screenshot = Screenshot(
                    file_path=file_path,
                    file_hash=file_hash,
                    file_size=file_size,
                    width=width,
                    height=height,
                    screen_id=screen_id,
                    app_name=app_name,
                    window_title=window_title,
                    event_id=event_id
                )
                
                session.add(screenshot)
                session.flush()  # 获取ID
                
                logging.debug(f"添加截图记录: {screenshot.id}")
                return screenshot.id
                
        except SQLAlchemyError as e:
            logging.error(f"添加截图记录失败: {e}")
            return None
    
    # 事件管理
    def _get_last_open_event(self, session: Session) -> Optional[Event]:
        """获取最后一个未结束的事件"""
        return session.query(Event).filter(Event.end_time.is_(None)).order_by(Event.start_time.desc()).first()
    
    def _calculate_title_similarity(self, title1: Optional[str], title2: Optional[str]) -> float:
        """计算两个标题的相似度（0-1）
        
        Args:
            title1: 第一个标题
            title2: 第二个标题
            
        Returns:
            相似度值（0.0-1.0）
        """
        if not title1 or not title2:
            return 0.0
        
        title1 = title1.strip()
        title2 = title2.strip()
        
        if not title1 or not title2:
            return 0.0
        
        # 完全相同
        if title1 == title2:
            return 1.0
        
        # 提取关键部分（对于浏览器标题，通常格式是 "页面标题 - 网站名"）
        def extract_key_parts(title):
            # 尝试提取网站名或应用主题
            if ' - ' in title:
                parts = title.split(' - ')
                # 返回最后一部分（通常是网站名或应用名）
                return parts[-1].lower().strip()
            elif '|' in title:
                parts = title.split('|')
                return parts[-1].lower().strip()
            return title.lower().strip()
        
        key1 = extract_key_parts(title1)
        key2 = extract_key_parts(title2)
        
        # 关键部分相同
        if key1 == key2:
            return 0.8
        
        # 计算字符串包含关系
        if key1 in key2 or key2 in key1:
            return 0.5
        
        # 计算共同词数量（简单相似度）
        words1 = set(key1.split())
        words2 = set(key2.split())
        if words1 and words2:
            common = words1 & words2
            union = words1 | words2
            if union:
                return len(common) / len(union)
        
        return 0.0
    
    def _should_reuse_event(self, old_app: Optional[str], old_title: Optional[str], 
                           new_app: Optional[str], new_title: Optional[str]) -> bool:
        """判断是否应该复用事件
        
        策略：
        1. 应用名不同 → 不复用
        2. 浏览器类应用 + 标题变化大 → 不复用
        3. 编辑器类应用 → 复用
        4. 其他应用 → 复用
        
        Args:
            old_app: 旧应用名
            old_title: 旧窗口标题
            new_app: 新应用名
            new_title: 新窗口标题
            
        Returns:
            是否应该复用事件
        """
        # 应用不同，不复用
        if (old_app or "").lower() != (new_app or "").lower():
            return False
        
        # 定义需要细粒度切分的应用（标题敏感应用）
        TITLE_SENSITIVE_APPS = [
            'chrome.exe', 'msedge.exe', 'firefox.exe', 'edge.exe',  # 浏览器
            'brave.exe', 'opera.exe', 'safari.exe',
            'explorer.exe',  # 文件管理器
            'wechat.exe', 'weixin.exe',  # 微信（聊天对象切换）
        ]
        
        app_lower = (new_app or "").lower()
        
        # 判断是否是标题敏感应用
        is_title_sensitive = any(app in app_lower for app in TITLE_SENSITIVE_APPS)
        
        if is_title_sensitive:
            # 对于浏览器等应用，检查标题变化
            similarity = self._calculate_title_similarity(old_title, new_title)
            # 相似度 < 0.3 认为是不同主题，创建新事件
            threshold = 0.3
            should_reuse = similarity >= threshold
            
            logging.debug(f"标题敏感应用 {app_lower}: 相似度={similarity:.2f}, 阈值={threshold}, 复用={should_reuse}")
            logging.debug(f"  旧标题: {old_title}")
            logging.debug(f"  新标题: {new_title}")
            
            return should_reuse
        
        # 其他应用（如VSCode、Word等）保持复用
        return True

    def get_or_create_event(self, app_name: Optional[str], window_title: Optional[str], timestamp: Optional[datetime] = None) -> Optional[int]:
        """按当前前台应用和窗口标题维护事件。
        
        智能切分策略：
        - 应用切换时创建新事件
        - 浏览器等标题敏感应用：标题变化大时创建新事件
        - 编辑器等应用：同一应用内保持同一事件
        
        Args:
            app_name: 应用名称
            window_title: 窗口标题
            timestamp: 时间戳
            
        Returns:
            事件ID
        """
        try:
            closed_event_id = None  # 记录被关闭的事件ID
            
            with self.get_session() as session:
                now_ts = timestamp or datetime.now()
                last_event = self._get_last_open_event(session)

                # 判断是否应该复用事件
                if last_event:
                    should_reuse = self._should_reuse_event(
                        old_app=last_event.app_name,
                        old_title=last_event.window_title,
                        new_app=app_name,
                        new_title=window_title
                    )
                    
                    if should_reuse:
                        # 复用事件，更新窗口标题
                        if window_title and window_title != last_event.window_title:
                            last_event.window_title = window_title
                        session.flush()
                        return last_event.id
                    else:
                        # 不复用，关闭旧事件
                        last_event.end_time = now_ts
                        closed_event_id = last_event.id
                        session.flush()
                        logging.info(f"关闭事件 {closed_event_id}: {last_event.app_name} - {last_event.window_title}")

                # 创建新事件
                new_event = Event(
                    app_name=app_name,
                    window_title=window_title,
                    start_time=now_ts
                )
                session.add(new_event)
                session.flush()
                new_event_id = new_event.id
                logging.info(f"创建新事件 {new_event_id}: {app_name} - {window_title}")
            
            # 在session关闭后，异步生成已关闭事件的摘要
            if closed_event_id:
                try:
                    from lifetrace_backend.event_summary_service import generate_event_summary_async
                    generate_event_summary_async(closed_event_id)
                except Exception as e:
                    logging.error(f"触发事件摘要生成失败: {e}")
            
            return new_event_id
        except SQLAlchemyError as e:
            logging.error(f"获取或创建事件失败: {e}")
            return None

    def close_active_event(self, end_time: Optional[datetime] = None) -> bool:
        """主动结束当前事件（可在程序退出时调用）"""
        try:
            closed_event_id = None
            with self.get_session() as session:
                last_event = self._get_last_open_event(session)
                if last_event and last_event.end_time is None:
                    last_event.end_time = end_time or datetime.now()
                    closed_event_id = last_event.id
                    session.flush()
            
            # 在session关闭后，异步生成已关闭事件的摘要
            if closed_event_id:
                try:
                    from lifetrace_backend.event_summary_service import generate_event_summary_async
                    generate_event_summary_async(closed_event_id)
                except Exception as e:
                    logging.error(f"触发事件摘要生成失败: {e}")
            
            return closed_event_id is not None
        except SQLAlchemyError as e:
            logging.error(f"结束事件失败: {e}")
            return False

    def update_event_summary(self, event_id: int, ai_title: str, ai_summary: str) -> bool:
        """
        更新事件的AI生成标题和摘要
        
        Args:
            event_id: 事件ID
            ai_title: AI生成的标题
            ai_summary: AI生成的摘要
            
        Returns:
            更新是否成功
        """
        try:
            with self.get_session() as session:
                event = session.query(Event).filter(Event.id == event_id).first()
                if event:
                    event.ai_title = ai_title
                    event.ai_summary = ai_summary
                    session.commit()
                    logging.info(f"事件 {event_id} AI摘要更新成功")
                    return True
                else:
                    logging.warning(f"事件 {event_id} 不存在")
                    return False
        except SQLAlchemyError as e:
            logging.error(f"更新事件AI摘要失败: {e}")
            return False

    def list_events(self, limit: int = 50, offset: int = 0,
                    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                    app_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出事件摘要（包含首张截图ID与截图数量）"""
        try:
            with self.get_session() as session:
                q = session.query(Event)
                if start_date:
                    q = q.filter(Event.start_time >= start_date)
                if end_date:
                    q = q.filter(Event.start_time <= end_date)
                if app_name:
                    q = q.filter(Event.app_name.like(f"%{app_name}%"))

                q = q.order_by(Event.start_time.desc()).offset(offset).limit(limit)
                events = q.all()

                results: List[Dict[str, Any]] = []
                for ev in events:
                    # 统计截图与首图
                    first_shot = session.query(Screenshot).filter(Screenshot.event_id == ev.id).order_by(Screenshot.created_at.asc()).first()
                    shot_count = session.query(Screenshot).filter(Screenshot.event_id == ev.id).count()
                    results.append({
                        'id': ev.id,
                        'app_name': ev.app_name,
                        'window_title': ev.window_title,
                        'start_time': ev.start_time,
                        'end_time': ev.end_time,
                        'screenshot_count': shot_count,
                        'first_screenshot_id': first_shot.id if first_shot else None,
                        'ai_title': ev.ai_title,
                        'ai_summary': ev.ai_summary
                    })
                return results
        except SQLAlchemyError as e:
            logging.error(f"列出事件失败: {e}")
            return []

    def get_event_screenshots(self, event_id: int) -> List[Dict[str, Any]]:
        """获取事件内截图列表"""
        try:
            with self.get_session() as session:
                shots = session.query(Screenshot).filter(Screenshot.event_id == event_id).order_by(Screenshot.created_at.asc()).all()
                return [{
                    'id': s.id,
                    'file_path': s.file_path,
                    'app_name': s.app_name,
                    'window_title': s.window_title,
                    'created_at': s.created_at,
                    'width': s.width,
                    'height': s.height
                } for s in shots]
        except SQLAlchemyError as e:
            logging.error(f"获取事件截图失败: {e}")
            return []

    def search_events_simple(self, query: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
        """基于SQLite的简单事件搜索（按OCR文本聚合）"""
        try:
            with self.get_session() as session:
                base_sql = """
                    SELECT e.id AS event_id,
                           e.app_name AS app_name,
                           e.window_title AS window_title,
                           e.start_time AS start_time,
                           e.end_time AS end_time,
                           MIN(s.id) AS first_screenshot_id,
                           COUNT(s.id) AS screenshot_count
                    FROM events e
                    JOIN screenshots s ON s.event_id = e.id
                    LEFT JOIN ocr_results o ON o.screenshot_id = s.id
                """
                where_clause = []
                params: Dict[str, Any] = {}
                if query:
                    where_clause.append("(o.text_content LIKE :q)")
                    params['q'] = f"%{query}%"

                sql = base_sql
                if where_clause:
                    sql += " WHERE " + " AND ".join(where_clause)
                sql += " GROUP BY e.id ORDER BY e.start_time DESC LIMIT :limit"
                params['limit'] = limit

                rows = session.execute(text(sql), params).fetchall()
                results = []
                for r in rows:
                    results.append({
                        'id': r.event_id,
                        'app_name': r.app_name,
                        'window_title': r.window_title,
                        'start_time': r.start_time,
                        'end_time': r.end_time,
                        'first_screenshot_id': r.first_screenshot_id,
                        'screenshot_count': r.screenshot_count
                    })
                return results
        except SQLAlchemyError as e:
            logging.error(f"搜索事件失败: {e}")
            return []

    def get_event_summary(self, event_id: int) -> Optional[Dict[str, Any]]:
        """获取单个事件的摘要信息"""
        try:
            with self.get_session() as session:
                ev = session.query(Event).filter(Event.id == event_id).first()
                if not ev:
                    return None
                first_shot = session.query(Screenshot).filter(Screenshot.event_id == ev.id).order_by(Screenshot.created_at.asc()).first()
                shot_count = session.query(Screenshot).filter(Screenshot.event_id == ev.id).count()
                return {
                    'id': ev.id,
                    'app_name': ev.app_name,
                    'window_title': ev.window_title,
                    'start_time': ev.start_time,
                    'end_time': ev.end_time,
                    'screenshot_count': shot_count,
                    'first_screenshot_id': first_shot.id if first_shot else None,
                    'ai_title': ev.ai_title,
                    'ai_summary': ev.ai_summary
                }
        except SQLAlchemyError as e:
            logging.error(f"获取事件摘要失败: {e}")
            return None

    def get_event_id_by_screenshot(self, screenshot_id: int) -> Optional[int]:
        """根据截图ID获取所属事件ID"""
        try:
            with self.get_session() as session:
                s = session.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
                return int(s.event_id) if s and s.event_id is not None else None
        except SQLAlchemyError as e:
            logging.error(f"查询截图所属事件失败: {e}")
            return None

    def get_event_text(self, event_id: int) -> str:
        """聚合事件下所有截图的OCR文本内容，按时间排序拼接"""
        try:
            with self.get_session() as session:
                from lifetrace_backend.models import OCRResult
                ocr_list = session.query(OCRResult).join(Screenshot, OCRResult.screenshot_id == Screenshot.id).\
                    filter(Screenshot.event_id == event_id).\
                    order_by(OCRResult.created_at.asc()).all()
                texts = [o.text_content for o in ocr_list if o and o.text_content]
                return "\n".join(texts)
        except SQLAlchemyError as e:
            logging.error(f"聚合事件文本失败: {e}")
            return ""
    
    def add_ocr_result(self, screenshot_id: int, text_content: str, confidence: float = 0.0,
                      language: str = 'ch', processing_time: float = 0.0) -> Optional[int]:
        """添加OCR结果"""
        try:
            with self.get_session() as session:
                ocr_result = OCRResult(
                    screenshot_id=screenshot_id,
                    text_content=text_content,
                    confidence=confidence,
                    language=language,
                    processing_time=processing_time
                )
                
                session.add(ocr_result)
                session.flush()
                
                # 更新截图处理状态
                screenshot = session.query(Screenshot).filter_by(id=screenshot_id).first()
                if screenshot:
                    screenshot.is_processed = True
                    screenshot.processed_at = datetime.now()
                
                logging.debug(f"添加OCR结果: {ocr_result.id}")
                return ocr_result.id
                
        except SQLAlchemyError as e:
            logging.error(f"添加OCR结果失败: {e}")
            return None
    
    def add_processing_task(self, screenshot_id: int, task_type: str = 'ocr') -> Optional[int]:
        """添加处理任务到队列"""
        try:
            with self.get_session() as session:
                # 检查是否已存在相同任务
                existing = session.query(ProcessingQueue).filter_by(
                    screenshot_id=screenshot_id,
                    task_type=task_type,
                    status='pending'
                ).first()
                
                if existing:
                    return existing.id
                
                task = ProcessingQueue(
                    screenshot_id=screenshot_id,
                    task_type=task_type
                )
                
                session.add(task)
                session.flush()
                
                logging.debug(f"添加处理任务: {task.id}")
                return task.id
                
        except SQLAlchemyError as e:
            logging.error(f"添加处理任务失败: {e}")
            return None
    
    def get_pending_tasks(self, task_type: str = 'ocr', limit: int = 10) -> List[ProcessingQueue]:
        """获取待处理任务"""
        try:
            with self.get_session() as session:
                tasks = session.query(ProcessingQueue).filter_by(
                    task_type=task_type,
                    status='pending'
                ).order_by(ProcessingQueue.created_at).limit(limit).all()
                
                # 分离对象，避免会话关闭后访问问题
                return [self._detach_task(task) for task in tasks]
                
        except SQLAlchemyError as e:
            logging.error(f"获取待处理任务失败: {e}")
            return []
    
    def _detach_task(self, task: ProcessingQueue) -> ProcessingQueue:
        """分离任务对象"""
        detached = ProcessingQueue()
        detached.id = task.id
        detached.screenshot_id = task.screenshot_id
        detached.task_type = task.task_type
        detached.status = task.status
        detached.retry_count = task.retry_count
        detached.error_message = task.error_message
        detached.created_at = task.created_at
        detached.updated_at = task.updated_at
        return detached
    
    def update_task_status(self, task_id: int, status: str, error_message: str = None):
        """更新任务状态"""
        try:
            with self.get_session() as session:
                task = session.query(ProcessingQueue).filter_by(id=task_id).first()
                if task:
                    task.status = status
                    task.updated_at = datetime.now()
                    
                    if status == 'failed':
                        task.retry_count += 1
                        task.error_message = error_message
                    
                    logging.debug(f"更新任务状态: {task_id} -> {status}")
                    
        except SQLAlchemyError as e:
            logging.error(f"更新任务状态失败: {e}")
    
    def get_screenshot_by_id(self, screenshot_id: int) -> Optional[dict]:
        """根据ID获取截图"""
        try:
            with self.get_session() as session:
                screenshot = session.query(Screenshot).filter_by(id=screenshot_id).first()
                if screenshot:
                    # 转换为字典避免会话分离问题
                    return {
                        'id': screenshot.id,
                        'file_path': screenshot.file_path,
                        'file_hash': screenshot.file_hash,
                        'file_size': screenshot.file_size,
                        'width': screenshot.width,
                        'height': screenshot.height,
                        'screen_id': screenshot.screen_id,
                        'app_name': screenshot.app_name,
                        'window_title': screenshot.window_title,
                        'created_at': screenshot.created_at,
                        'processed_at': screenshot.processed_at,
                        'is_processed': screenshot.is_processed
                    }
                return None
        except SQLAlchemyError as e:
            logging.error(f"获取截图失败: {e}")
            return None
    
    def get_screenshot_by_path(self, file_path: str) -> Optional[dict]:
        """根据文件路径获取截图"""
        try:
            with self.get_session() as session:
                screenshot = session.query(Screenshot).filter_by(file_path=file_path).first()
                if screenshot:
                    # 转换为字典避免会话分离问题
                    return {
                        'id': screenshot.id,
                        'file_path': screenshot.file_path,
                        'file_hash': screenshot.file_hash,
                        'file_size': screenshot.file_size,
                        'width': screenshot.width,
                        'height': screenshot.height,
                        'screen_id': screenshot.screen_id,
                        'app_name': screenshot.app_name,
                        'window_title': screenshot.window_title,
                        'created_at': screenshot.created_at,
                        'processed_at': screenshot.processed_at,
                        'is_processed': screenshot.is_processed
                    }
                return None
        except SQLAlchemyError as e:
            logging.error(f"根据路径获取截图失败: {e}")
            return None
    
    def update_screenshot_processed(self, screenshot_id: int):
        """更新截图处理状态"""
        try:
            with self.get_session() as session:
                screenshot = session.query(Screenshot).filter_by(id=screenshot_id).first()
                if screenshot:
                    screenshot.is_processed = True
                    screenshot.processed_at = datetime.now()
                    logging.debug(f"更新截图处理状态: {screenshot_id}")
                else:
                    logging.warning(f"未找到截图记录: {screenshot_id}")
        except SQLAlchemyError as e:
            logging.error(f"更新截图处理状态失败: {e}")
    
    def get_ocr_results_by_screenshot(self, screenshot_id: int) -> List[Dict[str, Any]]:
        """根据截图ID获取OCR结果"""
        try:
            with self.get_session() as session:
                ocr_results = session.query(OCRResult).filter_by(screenshot_id=screenshot_id).all()
                
                # 转换为字典列表
                results = []
                for ocr in ocr_results:
                    results.append({
                        'id': ocr.id,
                        'screenshot_id': ocr.screenshot_id,
                        'text_content': ocr.text_content,
                        'confidence': ocr.confidence,
                        'language': ocr.language,
                        'processing_time': ocr.processing_time,
                        'created_at': ocr.created_at
                    })
                
                return results
                
        except SQLAlchemyError as e:
            logging.error(f"获取OCR结果失败: {e}")
            return []
    
    def search_screenshots(self, query: str = None, start_date: datetime = None, 
                          end_date: datetime = None, app_name: str = None, 
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """搜索截图"""
        try:
            with self.get_session() as session:
                # 基础查询
                query_obj = session.query(
                    Screenshot,
                    OCRResult.text_content
                ).outerjoin(OCRResult, Screenshot.id == OCRResult.screenshot_id)
                
                # 添加条件
                if start_date:
                    query_obj = query_obj.filter(Screenshot.created_at >= start_date)
                
                if end_date:
                    query_obj = query_obj.filter(Screenshot.created_at <= end_date)
                
                if app_name:
                    query_obj = query_obj.filter(Screenshot.app_name.like(f"%{app_name}%"))
                
                if query:
                    query_obj = query_obj.filter(OCRResult.text_content.like(f"%{query}%"))
                
                # 应用分页：先排序，再应用offset和limit
                results = query_obj.order_by(Screenshot.created_at.desc()).offset(offset).limit(limit).all()
                
                # 格式化结果
                formatted_results = []
                for screenshot, text_content in results:
                    formatted_results.append({
                        'id': screenshot.id,
                        'file_path': screenshot.file_path,
                        'app_name': screenshot.app_name,
                        'window_title': screenshot.window_title,
                        'created_at': screenshot.created_at,
                        'text_content': text_content,
                        'width': screenshot.width,
                        'height': screenshot.height
                    })
                
                return formatted_results
                
        except SQLAlchemyError as e:
            logging.error(f"搜索截图失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            with self.get_session() as session:
                total_screenshots = session.query(Screenshot).count()
                processed_screenshots = session.query(Screenshot).filter_by(is_processed=True).count()
                pending_tasks = session.query(ProcessingQueue).filter_by(status='pending').count()
                
                # 今日统计
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_screenshots = session.query(Screenshot).filter(
                    Screenshot.created_at >= today_start
                ).count()
                
                return {
                    'total_screenshots': total_screenshots,
                    'processed_screenshots': processed_screenshots,
                    'pending_tasks': pending_tasks,
                    'today_screenshots': today_screenshots,
                    'processing_rate': processed_screenshots / max(total_screenshots, 1) * 100
                }
                
        except SQLAlchemyError as e:
            logging.error(f"获取统计信息失败: {e}")
            return {}
    
    def cleanup_old_data(self, max_days: int):
        """清理旧数据"""
        if max_days <= 0:
            return
            
        try:
            cutoff_date = datetime.now() - timedelta(days=max_days)
            
            with self.get_session() as session:
                # 获取要删除的截图
                old_screenshots = session.query(Screenshot).filter(
                    Screenshot.created_at < cutoff_date
                ).all()
                
                deleted_count = 0
                for screenshot in old_screenshots:
                    # 删除相关的OCR结果
                    session.query(OCRResult).filter_by(
                        screenshot_id=screenshot.id
                    ).delete()
                    
                    # 删除相关的搜索索引
                    session.query(SearchIndex).filter_by(
                        screenshot_id=screenshot.id
                    ).delete()
                    
                    # 删除相关的处理队列
                    session.query(ProcessingQueue).filter_by(
                        screenshot_id=screenshot.id
                    ).delete()
                    
                    # 删除文件
                    if os.path.exists(screenshot.file_path):
                        try:
                            os.remove(screenshot.file_path)
                        except Exception as e:
                            logging.error(f"删除文件失败 {screenshot.file_path}: {e}")
                    
                    # 删除截图记录
                    session.delete(screenshot)
                    deleted_count += 1
                
                logging.info(f"清理了 {deleted_count} 条旧数据")
                
        except SQLAlchemyError as e:
            logging.error(f"清理旧数据失败: {e}")

    def add_app_usage_log(self, app_name: str, window_title: str = None, 
                         duration_seconds: int = 0, screen_id: int = 0, 
                         timestamp: datetime = None) -> Optional[int]:
        """添加应用使用记录"""
        try:
            with self.get_session() as session:
                app_usage_log = AppUsageLog(
                    app_name=app_name,
                    window_title=window_title,
                    duration_seconds=duration_seconds,
                    screen_id=screen_id,
                    timestamp=timestamp or datetime.now()
                )
                session.add(app_usage_log)
                session.commit()
                return app_usage_log.id
        except SQLAlchemyError as e:
            logging.error(f"添加应用使用记录失败: {e}")
            return None

    def get_app_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取应用使用统计数据"""
        try:
            with self.get_session() as session:
                # 计算时间范围
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # 查询指定时间范围内的应用使用记录
                logs = session.query(AppUsageLog).filter(
                    AppUsageLog.timestamp >= start_date,
                    AppUsageLog.timestamp <= end_date
                ).all()
                
                # 按应用名称聚合数据
                app_usage_summary = {}
                daily_usage = {}
                hourly_usage = {}
                
                for log in logs:
                    app_name = log.app_name
                    date_str = log.timestamp.strftime('%Y-%m-%d')
                    hour = log.timestamp.hour
                    
                    # 应用使用汇总
                    if app_name not in app_usage_summary:
                        app_usage_summary[app_name] = {
                            'app_name': app_name,
                            'total_time': 0,
                            'session_count': 0,
                            'last_used': log.timestamp
                        }
                    
                    app_usage_summary[app_name]['total_time'] += log.duration_seconds
                    app_usage_summary[app_name]['session_count'] += 1
                    if log.timestamp > app_usage_summary[app_name]['last_used']:
                        app_usage_summary[app_name]['last_used'] = log.timestamp
                    
                    # 每日使用统计
                    if date_str not in daily_usage:
                        daily_usage[date_str] = {}
                    if app_name not in daily_usage[date_str]:
                        daily_usage[date_str][app_name] = 0
                    daily_usage[date_str][app_name] += log.duration_seconds
                    
                    # 小时使用统计
                    if hour not in hourly_usage:
                        hourly_usage[hour] = {}
                    if app_name not in hourly_usage[hour]:
                        hourly_usage[hour][app_name] = 0
                    hourly_usage[hour][app_name] += log.duration_seconds
                
                return {
                    'app_usage_summary': app_usage_summary,
                    'daily_usage': daily_usage,
                    'hourly_usage': hourly_usage,
                    'total_apps': len(app_usage_summary),
                    'total_time': sum(app['total_time'] for app in app_usage_summary.values())
                }
                
        except SQLAlchemyError as e:
            logging.error(f"获取应用使用统计失败: {e}")
            return {
                'app_usage_summary': {},
                'daily_usage': {},
                'hourly_usage': {},
                'total_apps': 0,
                'total_time': 0
            }


# 全局数据库管理器实例
db_manager = DatabaseManager()