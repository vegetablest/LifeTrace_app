import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.simple_ocr import SimpleOCRProcessor
from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.multimodal_vector_service import create_multimodal_vector_service
from lifetrace_backend.logging_config import setup_logging

# 导入系统资源分析模块
import psutil
import sys
import json
from pathlib import Path
from datetime import datetime

# 设置日志系统
logger_manager = setup_logging(config)
logger = logger_manager.get_server_logger()


# Pydantic模型
class SearchRequest(BaseModel):
    query: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    app_name: Optional[str] = None
    limit: int = 50

class ScreenshotResponse(BaseModel):
    id: int
    file_path: str
    app_name: Optional[str]
    window_title: Optional[str]
    created_at: datetime
    text_content: Optional[str]
    width: int
    height: int

class EventResponse(BaseModel):
    id: int
    app_name: Optional[str]
    window_title: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    screenshot_count: int
    first_screenshot_id: Optional[int]

class EventDetailResponse(BaseModel):
    id: int
    app_name: Optional[str]
    window_title: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    screenshots: List[ScreenshotResponse]

class StatisticsResponse(BaseModel):
    total_screenshots: int
    processed_screenshots: int
    pending_tasks: int
    today_screenshots: int
    processing_rate: float

class ConfigResponse(BaseModel):
    base_dir: str
    screenshots_dir: str
    database_path: str
    server: Dict[str, Any]
    record: Dict[str, Any]
    ocr: Dict[str, Any]
    storage: Dict[str, Any]

class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    use_rerank: bool = True
    retrieve_k: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None

class SemanticSearchResult(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]
    ocr_result: Optional[Dict[str, Any]] = None
    screenshot: Optional[Dict[str, Any]] = None

class MultimodalSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    text_weight: Optional[float] = None
    image_weight: Optional[float] = None
    filters: Optional[Dict[str, Any]] = None

class MultimodalSearchResult(BaseModel):
    text: str
    combined_score: float
    text_score: float
    image_score: float
    text_weight: float
    image_weight: float
    metadata: Dict[str, Any]
    ocr_result: Optional[Dict[str, Any]] = None
    screenshot: Optional[Dict[str, Any]] = None

class VectorStatsResponse(BaseModel):
    enabled: bool
    collection_name: Optional[str] = None
    document_count: Optional[int] = None
    error: Optional[str] = None

class MultimodalStatsResponse(BaseModel):
    enabled: bool
    multimodal_available: bool
    text_weight: float
    image_weight: float
    text_database: Dict[str, Any]
    image_database: Dict[str, Any]
    error: Optional[str] = None

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cmdline: str
    memory_mb: float
    memory_vms_mb: float
    cpu_percent: float

class SystemResourcesResponse(BaseModel):
    memory: Dict[str, float]
    cpu: Dict[str, Any]
    disk: Dict[str, Dict[str, float]]
    lifetrace_processes: List[ProcessInfo]
    storage: Dict[str, Any]
    summary: Dict[str, Any]
    timestamp: datetime


# 创建FastAPI应用
app = FastAPI(
    title="LifeTrace API",
    description="智能生活记录系统 API",
    version="0.1.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8840", "http://127.0.0.1:8840"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件和模板
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    templates = None

# 初始化OCR处理器
ocr_processor = SimpleOCRProcessor()

# 初始化向量数据库服务
vector_service = create_vector_service(config, db_manager)

# 初始化多模态向量数据库服务
multimodal_vector_service = create_multimodal_vector_service(config, db_manager)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("""
        <html>
            <head><title>LifeTrace</title></head>
            <body>
                <h1>LifeTrace 智能生活记录系统</h1>
                <p><a href="/api/docs">API 文档</a></p>
                <p><a href="/api/screenshots">查看截图</a></p>
                <p><a href="/api/statistics">系统统计</a></p>
            </body>
        </html>
        """)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "connected" if db_manager.engine else "disconnected",
        "ocr": "available" if ocr_processor.is_available() else "unavailable"
    }


@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """获取系统统计信息"""
    stats = db_manager.get_statistics()
    return StatisticsResponse(**stats)


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """获取配置信息"""
    return ConfigResponse(
        base_dir=config.base_dir,
        screenshots_dir=config.screenshots_dir,
        database_path=config.database_path,
        server={
            "host": config.get("server.host"),
            "port": config.get("server.port"),
            "debug": config.get("server.debug", False)
        },
        record={
            "interval": config.get("record.interval"),
            "screens": config.get("record.screens"),
            "format": config.get("record.format")
        },
        ocr={
            "enabled": config.get("ocr.enabled"),
            "use_gpu": config.get("ocr.use_gpu"),
            "language": config.get("ocr.language"),
            "confidence_threshold": config.get("ocr.confidence_threshold")
        },
        storage={
            "max_days": config.get("storage.max_days"),
            "deduplicate": config.get("storage.deduplicate"),
            "hash_threshold": config.get("storage.hash_threshold")
        }
    )


@app.post("/api/search", response_model=List[ScreenshotResponse])
async def search_screenshots(search_request: SearchRequest):
    """搜索截图"""
    try:
        results = db_manager.search_screenshots(
            query=search_request.query,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            app_name=search_request.app_name,
            limit=search_request.limit
        )
        
        return [ScreenshotResponse(**result) for result in results]
        
    except Exception as e:
        logging.error(f"搜索截图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screenshots", response_model=List[ScreenshotResponse])
async def get_screenshots(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    app_name: Optional[str] = Query(None)
):
    """获取截图列表"""
    try:
        # 解析日期
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        # 搜索截图
        results = db_manager.search_screenshots(
            start_date=start_dt,
            end_date=end_dt,
            app_name=app_name,
            limit=limit
        )
        
        # 应用偏移
        if offset > 0:
            results = results[offset:]
        
        return [ScreenshotResponse(**result) for result in results]
        
    except Exception as e:
        logging.error(f"获取截图列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events", response_model=List[EventResponse])
async def list_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    app_name: Optional[str] = Query(None)
):
    """获取事件列表（事件=前台应用使用阶段），用于事件级别展示与检索"""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        events = db_manager.list_events(limit=limit, offset=offset, start_date=start_dt, end_date=end_dt, app_name=app_name)
        return [EventResponse(**e) for e in events]
    except Exception as e:
        logging.error(f"获取事件列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/{event_id}", response_model=EventDetailResponse)
async def get_event_detail(event_id: int):
    """获取事件详情（包含该事件下的截图列表）"""
    try:
        # 读取事件摘要
        event_summary = db_manager.get_event_summary(event_id)
        if not event_summary:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 读取截图
        screenshots = db_manager.get_event_screenshots(event_id)
        screenshots_resp = [ScreenshotResponse(
            id=s['id'],
            file_path=s['file_path'],
            app_name=s['app_name'],
            window_title=s['window_title'],
            created_at=s['created_at'],
            text_content=None,
            width=s['width'],
            height=s['height']
        ) for s in screenshots]

        return EventDetailResponse(
            id=event_summary['id'],
            app_name=event_summary['app_name'],
            window_title=event_summary['window_title'],
            start_time=event_summary['start_time'],
            end_time=event_summary['end_time'],
            screenshots=screenshots_resp
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取事件详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/event-search", response_model=List[EventResponse])
async def search_events(search_request: SearchRequest):
    """事件级简单文本搜索：按OCR分组后返回事件摘要"""
    try:
        results = db_manager.search_events_simple(
            query=search_request.query,
            limit=search_request.limit
        )
        return [EventResponse(**r) for r in results]
    except Exception as e:
        logging.error(f"搜索事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screenshots/{screenshot_id}")
async def get_screenshot(screenshot_id: int):
    """获取单个截图详情"""
    screenshot = db_manager.get_screenshot_by_id(screenshot_id)
    
    if not screenshot:
        raise HTTPException(status_code=404, detail="截图不存在")
    
    # 获取OCR结果
    ocr_data = None
    try:
        with db_manager.get_session() as session:
            from .models import OCRResult
            ocr_result = session.query(OCRResult).filter_by(
                screenshot_id=screenshot_id
            ).first()
            
            # 在session内提取数据
            if ocr_result:
                ocr_data = {
                    "text_content": ocr_result.text_content,
                    "confidence": ocr_result.confidence,
                    "language": ocr_result.language,
                    "processing_time": ocr_result.processing_time
                }
    except Exception as e:
        logging.warning(f"获取OCR结果失败: {e}")
    
    # screenshot已经是字典格式，直接使用
    result = screenshot.copy()
    result["ocr_result"] = ocr_data
    
    return result


@app.get("/api/screenshots/{screenshot_id}/image")
async def get_screenshot_image(screenshot_id: int):
    """获取截图图片文件"""
    screenshot = db_manager.get_screenshot_by_id(screenshot_id)
    
    if not screenshot:
        raise HTTPException(status_code=404, detail="截图不存在")
    
    file_path = screenshot['file_path']
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"screenshot_{screenshot_id}.png"
    )


@app.post("/api/ocr/process")
async def process_ocr(screenshot_id: int):
    """手动触发OCR处理"""
    if not ocr_processor.is_available():
        raise HTTPException(status_code=503, detail="OCR服务不可用")
    
    screenshot = db_manager.get_screenshot_by_id(screenshot_id)
    if not screenshot:
        raise HTTPException(status_code=404, detail="截图不存在")
    
    if screenshot['is_processed']:
        raise HTTPException(status_code=400, detail="截图已经处理过")
    
    try:
        # 执行OCR处理
        ocr_result = ocr_processor.process_image(screenshot['file_path'])
        
        if ocr_result['success']:
            # 保存OCR结果
            db_manager.add_ocr_result(
                screenshot_id=screenshot['id'],
                text_content=ocr_result['text_content'],
                confidence=ocr_result['confidence'],
                language=ocr_result.get('language', 'ch'),
                processing_time=ocr_result['processing_time']
            )
            
            return {
                "success": True,
                "text_content": ocr_result['text_content'],
                "confidence": ocr_result['confidence'],
                "processing_time": ocr_result['processing_time']
            }
        else:
            raise HTTPException(status_code=500, detail=ocr_result['error'])
            
    except Exception as e:
        logging.error(f"OCR处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ocr/statistics")
async def get_ocr_statistics():
    """获取OCR处理统计"""
    return ocr_processor.get_statistics()


@app.post("/api/cleanup")
async def cleanup_old_data(days: int = Query(30, ge=1)):
    """清理旧数据"""
    try:
        db_manager.cleanup_old_data(days)
        return {"success": True, "message": f"清理了 {days} 天前的数据"}
    except Exception as e:
        logging.error(f"清理数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queue/status")
async def get_queue_status():
    """获取处理队列状态"""
    try:
        with db_manager.get_session() as session:
            from .models import ProcessingQueue
            
            pending_count = session.query(ProcessingQueue).filter_by(status='pending').count()
            processing_count = session.query(ProcessingQueue).filter_by(status='processing').count()
            completed_count = session.query(ProcessingQueue).filter_by(status='completed').count()
            failed_count = session.query(ProcessingQueue).filter_by(status='failed').count()
            
            return {
                "pending": pending_count,
                "processing": processing_count,
                "completed": completed_count,
                "failed": failed_count,
                "total": pending_count + processing_count + completed_count + failed_count
            }
            
    except Exception as e:
        logging.error(f"获取队列状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/semantic-search", response_model=List[SemanticSearchResult])
async def semantic_search(request: SemanticSearchRequest):
    """语义搜索 OCR 结果"""
    try:
        if not vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="向量数据库服务不可用")
        
        results = vector_service.semantic_search(
            query=request.query,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
            retrieve_k=request.retrieve_k,
            filters=request.filters
        )
        
        # 转换为响应格式
        search_results = []
        for result in results:
            search_result = SemanticSearchResult(
                text=result.get('text', ''),
                score=result.get('score', 0.0),
                metadata=result.get('metadata', {}),
                ocr_result=result.get('ocr_result'),
                screenshot=result.get('screenshot')
            )
            search_results.append(search_result)
        
        return search_results
        
    except Exception as e:
        logging.error(f"语义搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/event-semantic-search", response_model=List[EventResponse])
async def event_semantic_search(request: SemanticSearchRequest):
    """事件级语义搜索（基于事件聚合文本）"""
    try:
        if not vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="向量数据库服务不可用")
        raw_results = vector_service.semantic_search_events(
            query=request.query,
            top_k=request.top_k
        )

        # semantic_search_events 现在直接返回格式化的事件数据
        events_resp: List[EventResponse] = []
        for event_data in raw_results:
            # 检查是否已经是完整的事件数据格式
            if 'id' in event_data and 'app_name' in event_data:
                # 直接使用返回的事件数据
                events_resp.append(EventResponse(**event_data))
            else:
                # 向后兼容：如果是旧格式，使用原来的逻辑
                metadata = event_data.get('metadata', {})
                event_id = metadata.get('event_id')
                if not event_id:
                    continue
                matched = db_manager.get_event_summary(int(event_id))
                if matched:
                    events_resp.append(EventResponse(**matched))

        return events_resp
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"事件语义搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/multimodal-search", response_model=List[MultimodalSearchResult])
async def multimodal_search(request: MultimodalSearchRequest):
    """多模态搜索 (图像+文本)"""
    try:
        if not multimodal_vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="多模态向量数据库服务不可用")
        
        results = multimodal_vector_service.multimodal_search(
            query=request.query,
            top_k=request.top_k,
            text_weight=request.text_weight,
            image_weight=request.image_weight,
            filters=request.filters
        )
        
        # 转换为响应格式
        search_results = []
        for result in results:
            search_result = MultimodalSearchResult(
                text=result.get('text', ''),
                combined_score=result.get('combined_score', 0.0),
                text_score=result.get('text_score', 0.0),
                image_score=result.get('image_score', 0.0),
                text_weight=result.get('text_weight', 0.6),
                image_weight=result.get('image_weight', 0.4),
                metadata=result.get('metadata', {}),
                ocr_result=result.get('ocr_result'),
                screenshot=result.get('screenshot')
            )
            search_results.append(search_result)
        
        return search_results
        
    except Exception as e:
        logging.error(f"多模态搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vector-stats", response_model=VectorStatsResponse)
async def get_vector_stats():
    """获取向量数据库统计信息"""
    try:
        stats = vector_service.get_stats()
        return VectorStatsResponse(**stats)
        
    except Exception as e:
        logging.error(f"获取向量数据库统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multimodal-stats", response_model=MultimodalStatsResponse)
async def get_multimodal_stats():
    """获取多模态向量数据库统计信息"""
    try:
        stats = multimodal_vector_service.get_stats()
        return MultimodalStatsResponse(**stats)
        
    except Exception as e:
        logging.error(f"获取多模态统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/multimodal-sync")
async def sync_multimodal_database(
    limit: Optional[int] = Query(None, description="同步的最大记录数"),
    force_reset: bool = Query(False, description="是否强制重置多模态向量数据库")
):
    """同步 SQLite 数据库到多模态向量数据库"""
    try:
        if not multimodal_vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="多模态向量数据库服务不可用")
        
        synced_count = multimodal_vector_service.sync_from_database(limit=limit, force_reset=force_reset)
        
        return {
            "message": "多模态同步完成",
            "synced_count": synced_count
        }
        
    except Exception as e:
        logging.error(f"多模态同步失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vector-sync")
async def sync_vector_database(
    limit: Optional[int] = Query(None, description="同步的最大记录数"),
    force_reset: bool = Query(False, description="是否强制重置向量数据库")
):
    """同步 SQLite 数据库到向量数据库"""
    try:
        if not vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="向量数据库服务不可用")
        
        synced_count = vector_service.sync_from_database(limit=limit, force_reset=force_reset)
        
        return {
            "message": "同步完成",
            "synced_count": synced_count
        }
        
    except Exception as e:
        logging.error(f"向量数据库同步失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vector-reset")
async def reset_vector_database():
    """重置向量数据库"""
    try:
        if not vector_service.is_enabled():
            raise HTTPException(status_code=503, detail="向量数据库服务不可用")
        
        success = vector_service.reset()
        
        if success:
            return {"message": "向量数据库重置成功"}
        else:
            raise HTTPException(status_code=500, detail="向量数据库重置失败")
        
    except Exception as e:
        logging.error(f"向量数据库重置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 系统资源监控路由
@app.get("/system-monitor", response_class=HTMLResponse)
async def system_monitor_page(request: Request):
    """系统资源监控页面"""
    # 直接返回HTML内容，不使用模板
    return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LifeTrace 系统资源监控</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #333; }
                .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; min-width: 150px; }
                .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
                .metric-label { font-size: 14px; color: #666; }
                .process-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                .process-table th, .process-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .process-table th { background-color: #f8f9fa; }
                .status-good { color: #28a745; }
                .status-warning { color: #ffc107; }
                .status-danger { color: #dc3545; }
                .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                .refresh-btn:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">LifeTrace 系统资源监控</h1>
                <div class="card">
                    <button class="refresh-btn" onclick="loadSystemResources()">刷新数据</button>
                    <div id="system-resources">加载中...</div>
                </div>
            </div>
            <script>
                async function loadSystemResources() {
                    try {
                        const response = await fetch('/api/system-resources');
                        const data = await response.json();
                        displaySystemResources(data);
                    } catch (error) {
                        document.getElementById('system-resources').innerHTML = '<p style="color: red;">加载失败: ' + error.message + '</p>';
                    }
                }
                
                function displaySystemResources(data) {
                    const container = document.getElementById('system-resources');
                    const timestamp = new Date(data.timestamp).toLocaleString('zh-CN');
                    
                    let html = `
                        <p><strong>更新时间:</strong> ${timestamp}</p>
                        
                        <h3>系统整体资源</h3>
                        <div>
                            <div class="metric">
                                <div class="metric-value">${data.memory.percent.toFixed(1)}%</div>
                                <div class="metric-label">内存使用率</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.memory.used_gb.toFixed(1)}GB</div>
                                <div class="metric-label">已用内存</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.cpu.percent.toFixed(1)}%</div>
                                <div class="metric-label">CPU使用率</div>
                            </div>
                        </div>
                        
                        <h3>LifeTrace 进程 (${data.lifetrace_processes.length}个)</h3>
                        <table class="process-table">
                            <thead>
                                <tr>
                                    <th>PID</th>
                                    <th>进程名</th>
                                    <th>内存(MB)</th>
                                    <th>CPU(%)</th>
                                    <th>命令行</th>
                                </tr>
                            </thead>
                            <tbody>`;
                    
                    data.lifetrace_processes.forEach(proc => {
                        const memoryClass = proc.memory_mb > 500 ? 'status-danger' : proc.memory_mb > 200 ? 'status-warning' : 'status-good';
                        const cpuClass = proc.cpu_percent > 50 ? 'status-danger' : proc.cpu_percent > 20 ? 'status-warning' : 'status-good';
                        
                        html += `
                            <tr>
                                <td>${proc.pid}</td>
                                <td>${proc.name}</td>
                                <td class="${memoryClass}">${proc.memory_mb.toFixed(1)}</td>
                                <td class="${cpuClass}">${proc.cpu_percent.toFixed(1)}</td>
                                <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">${proc.cmdline}</td>
                            </tr>`;
                    });
                    
                    html += `
                            </tbody>
                        </table>
                        
                        <h3>资源使用总结</h3>
                        <div>
                            <div class="metric">
                                <div class="metric-value">${data.summary.total_memory_mb.toFixed(1)}MB</div>
                                <div class="metric-label">LifeTrace总内存</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.summary.total_cpu_percent.toFixed(1)}%</div>
                                <div class="metric-label">LifeTrace总CPU</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.summary.total_storage_mb.toFixed(1)}MB</div>
                                <div class="metric-label">数据存储</div>
                            </div>
                        </div>
                        
                        <h3>磁盘使用情况</h3>
                        <table class="process-table">
                            <thead>
                                <tr>
                                    <th>磁盘</th>
                                    <th>总容量(GB)</th>
                                    <th>已用(GB)</th>
                                    <th>可用(GB)</th>
                                    <th>使用率</th>
                                </tr>
                            </thead>
                            <tbody>`;
                    
                    Object.entries(data.disk).forEach(([device, usage]) => {
                        const percentClass = usage.percent > 90 ? 'status-danger' : usage.percent > 70 ? 'status-warning' : 'status-good';
                        html += `
                            <tr>
                                <td>${device}</td>
                                <td>${usage.total_gb.toFixed(1)}</td>
                                <td>${usage.used_gb.toFixed(1)}</td>
                                <td>${usage.free_gb.toFixed(1)}</td>
                                <td class="${percentClass}">${usage.percent.toFixed(1)}%</td>
                            </tr>`;
                    });
                    
                    html += `
                            </tbody>
                        </table>`;
                    
                    container.innerHTML = html;
                }
                
                // 页面加载时自动刷新数据
                loadSystemResources();
                
                // 每30秒自动刷新
                setInterval(loadSystemResources, 30000);
            </script>
        </body>
        </html>
        """)


@app.get("/api/system-resources", response_model=SystemResourcesResponse)
async def get_system_resources():
    """获取系统资源使用情况"""
    try:
        # 获取LifeTrace相关进程
        lifetrace_processes = []
        total_memory = 0
        total_cpu = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                if any(keyword in cmdline.lower() for keyword in [
                    'lifetrace', 'recorder.py', 'processor.py', 'server.py', 
                    'start_all_services.py', 'start_ocr_service.py'
                ]):
                    # 使用非阻塞的CPU百分比获取，避免卡死
                    try:
                        cpu_percent = proc.cpu_percent(interval=None)  # 非阻塞调用
                    except:
                        cpu_percent = 0.0
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    memory_vms_mb = proc.info['memory_info'].vms / 1024 / 1024
                    
                    process_info = ProcessInfo(
                        pid=proc.info['pid'],
                        name=proc.info['name'],
                        cmdline=cmdline,
                        memory_mb=memory_mb,
                        memory_vms_mb=memory_vms_mb,
                        cpu_percent=cpu_percent
                    )
                    lifetrace_processes.append(process_info)
                    total_memory += memory_mb
                    total_cpu += cpu_percent
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 获取系统资源信息
        memory = psutil.virtual_memory()
        # 使用非阻塞的CPU百分比获取，避免卡死
        cpu_percent = psutil.cpu_percent(interval=None)  # 非阻塞调用
        cpu_count = psutil.cpu_count()
        
        # 获取磁盘信息
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    'total_gb': usage.total / 1024**3,
                    'used_gb': usage.used / 1024**3,
                    'free_gb': usage.free / 1024**3,
                    'percent': (usage.used / usage.total) * 100
                }
            except PermissionError:
                continue
        
        # 获取数据库和截图存储信息
        db_path = Path.home() / '.lifetrace' / 'lifetrace.db'
        db_size_mb = db_path.stat().st_size / 1024 / 1024 if db_path.exists() else 0
        
        screenshots_path = Path.home() / '.lifetrace' / 'screenshots'
        screenshots_size_mb = 0
        screenshots_count = 0
        if screenshots_path.exists():
            for file_path in screenshots_path.glob('*.png'):
                if file_path.is_file():
                    screenshots_size_mb += file_path.stat().st_size / 1024 / 1024
                    screenshots_count += 1
        
        total_storage_mb = db_size_mb + screenshots_size_mb
        
        return SystemResourcesResponse(
            memory={
                'total_gb': memory.total / 1024**3,
                'available_gb': memory.available / 1024**3,
                'used_gb': (memory.total - memory.available) / 1024**3,
                'percent': memory.percent
            },
            cpu={
                'percent': cpu_percent,
                'count': cpu_count
            },
            disk=disk_usage,
            lifetrace_processes=lifetrace_processes,
            storage={
                'database_mb': db_size_mb,
                'screenshots_mb': screenshots_size_mb,
                'screenshots_count': screenshots_count,
                'total_mb': total_storage_mb
            },
            summary={
                'total_memory_mb': total_memory,
                'total_cpu_percent': total_cpu,
                'process_count': len(lifetrace_processes),
                'total_storage_mb': total_storage_mb
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logging.error(f"获取系统资源信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 日志查看路由
@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """日志查看页面"""
    if templates is not None:
        return templates.TemplateResponse("logs.html", {"request": request})
    else:
        return HTMLResponse("<h1>模板系统未初始化</h1>", status_code=500)

@app.get("/api/logs/files")
async def get_log_files():
    """获取日志文件列表"""
    try:
        logs_dir = Path(config.base_dir) / "logs"
        if not logs_dir.exists():
            return []
        
        log_files = []
        # 递归扫描所有子目录中的.log文件
        for file_path in logs_dir.rglob("*.log"):
            # 获取相对于logs目录的路径
            relative_path = file_path.relative_to(logs_dir)
            # 获取文件大小
            file_size = file_path.stat().st_size
            size_str = f"{file_size // 1024}KB" if file_size > 1024 else f"{file_size}B"
            
            log_files.append({
                "name": str(relative_path),
                "path": str(file_path),
                "size": size_str,
                "category": relative_path.parent.name if relative_path.parent.name != '.' else 'root'
            })
        
        return sorted(log_files, key=lambda x: x["name"])
    except Exception as e:
        logger.error(f"获取日志文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/content", response_class=PlainTextResponse)
async def get_log_content(file: str = Query(..., description="日志文件相对路径")):
    """获取日志文件内容"""
    try:
        logs_dir = Path(config.base_dir) / "logs"
        log_file = logs_dir / file
        
        # 安全检查：确保文件在logs目录内
        if not str(log_file.resolve()).startswith(str(logs_dir.resolve())):
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        # 读取文件内容（最后1000行）
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 只返回最后1000行，避免内存问题
            if len(lines) > 1000:
                lines = lines[-1000:]
            return ''.join(lines)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))





def main():
    """主函数 - 命令行入口"""
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description='LifeTrace Web Server')
    parser.add_argument('--host', default='127.0.0.1', help='服务器地址')
    parser.add_argument('--port', type=int, default=8840, help='服务器端口')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 日志已在模块顶部通过logging_config配置
    
    # 使用配置中的服务器设置，但命令行参数优先
    host = args.host or config.get('server.host', '127.0.0.1')
    port = args.port or config.get('server.port', 8840)
    debug = args.debug or config.get('server.debug', False)
    
    logging.info(f"启动LifeTrace Web服务器: http://{host}:{port}")
    
    # 启动服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        access_log=debug
    )


if __name__ == '__main__':
    main()