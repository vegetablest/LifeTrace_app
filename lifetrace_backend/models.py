from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

def get_local_time():
    """获取本地时间"""
    return datetime.datetime.now()

Base = declarative_base()

class Event(Base):
    """事件模型（按前台应用连续使用区间聚合截图）"""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(200))
    window_title = Column(String(500))  # 首个或最近的窗口标题
    start_time = Column(DateTime, default=get_local_time)
    end_time = Column(DateTime)  # 事件结束时间（应用切换时填充）
    created_at = Column(DateTime, default=get_local_time)

    def __repr__(self):
        return f"<Event(id={self.id}, app={self.app_name})>"

class Screenshot(Base):
    """截图记录模型"""
    __tablename__ = 'screenshots'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), nullable=False, unique=True)
    file_hash = Column(String(64), nullable=False)  # imagehash值
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    screen_id = Column(Integer, nullable=False, default=0)
    app_name = Column(String(200))  # 前台应用名称
    window_title = Column(String(500))  # 窗口标题
    # 事件ID（可为空，老数据迁移后逐步填充）
    event_id = Column(Integer)
    created_at = Column(DateTime, default=get_local_time)
    processed_at = Column(DateTime)  # OCR处理时间
    is_processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Screenshot(id={self.id}, file={self.file_path})>"

class OCRResult(Base):
    """OCR结果模型"""
    __tablename__ = 'ocr_results'
    
    id = Column(Integer, primary_key=True)
    screenshot_id = Column(Integer, nullable=False)
    text_content = Column(Text)  # 提取的文本内容
    confidence = Column(Float)  # 置信度
    language = Column(String(10))  # 识别语言
    processing_time = Column(Float)  # 处理耗时（秒）
    created_at = Column(DateTime, default=get_local_time)
    
    def __repr__(self):
        return f"<OCRResult(id={self.id}, screenshot_id={self.screenshot_id})>"

class SearchIndex(Base):
    """搜索索引模型"""
    __tablename__ = 'search_index'
    
    id = Column(Integer, primary_key=True)
    screenshot_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # 用于搜索的内容
    keywords = Column(Text)  # 关键词（JSON格式）
    created_at = Column(DateTime, default=get_local_time)
    
    def __repr__(self):
        return f"<SearchIndex(id={self.id}, screenshot_id={self.screenshot_id})>"

class ProcessingQueue(Base):
    """处理队列模型"""
    __tablename__ = 'processing_queue'
    
    id = Column(Integer, primary_key=True)
    screenshot_id = Column(Integer, nullable=False)
    task_type = Column(String(50), nullable=False)  # 任务类型：ocr
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    def __repr__(self):
        return f"<ProcessingQueue(id={self.id}, task={self.task_type}, status={self.status})>"