"""查询解析器模块

将自然语言查询转换为结构化的数据库查询条件。
使用LLM理解用户意图并提取查询参数。
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .app_mapping import app_mapper


@dataclass
class QueryConditions:
    """查询条件数据类"""

    # 时间范围
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # 应用过滤
    app_names: Optional[List[str]] = None

    # 文本内容
    keywords: Optional[List[str]] = None

    # 其他条件
    limit: int = 1000

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {}

        if self.start_date:
            result["start_date"] = self.start_date
        if self.end_date:
            result["end_date"] = self.end_date
        if self.app_names:
            result["app_names"] = self.app_names
        if self.keywords:
            result["keywords"] = self.keywords
        if self.limit:
            result["limit"] = self.limit

        return result


class QueryParser:
    """查询解析器"""

    def __init__(self, llm_client=None):
        self.logger = logging.getLogger(__name__)
        self.llm_client = llm_client

        # 应用名称映射（常见的应用别名）
        self.app_name_mapping = {
            "微信": ["WeChat", "wechat", "微信"],
            "QQ": ["QQ", "qq", "TencentQQ"],
            "浏览器": [
                "Chrome",
                "Firefox",
                "Edge",
                "Safari",
                "chrome",
                "firefox",
                "edge",
            ],
            "VS Code": ["Code", "vscode", "Visual Studio Code"],
            "记事本": ["Notepad", "notepad"],
            "Word": ["WINWORD", "Microsoft Word", "word"],
            "Excel": ["EXCEL", "Microsoft Excel", "excel"],
            "PowerPoint": ["POWERPNT", "Microsoft PowerPoint", "powerpoint", "ppt"],
        }

        # 时间关键词映射
        self.time_keywords = {
            "今天": 0,
            "昨天": 1,
            "前天": 2,
            "本周": 7,
            "上周": 14,
            "本月": 30,
            "上月": 60,
        }

    def parse_query(self, query: str) -> QueryConditions:
        """解析自然语言查询

        Args:
            query: 自然语言查询字符串

        Returns:
            QueryConditions: 解析后的查询条件
        """
        self.logger.info(f"解析查询: {query}")

        # 如果有LLM客户端，使用LLM解析
        if self.llm_client:
            try:
                parsed_data = self.llm_client.parse_query(query)

                # 检查LLM解析结果是否有效（至少有一个有用的字段）
                has_keywords = (
                    parsed_data.get("keywords") and len(parsed_data["keywords"]) > 0
                )
                has_app_names = (
                    parsed_data.get("app_names") and len(parsed_data["app_names"]) > 0
                )
                has_time_info = parsed_data.get("start_date") or parsed_data.get(
                    "end_date"
                )

                if has_keywords or has_app_names or has_time_info:
                    print("LLM解析结果有效，构建QueryConditions")
                    try:
                        result = self._build_query_conditions(parsed_data)
                        print("\n=== 最终查询条件 (LLM解析) ===")
                        print(f"查询条件: {result}")
                        return result
                    except Exception as e:
                        self.logger.warning(f"构建查询条件失败: {e}")
                        pass
                else:
                    print("缺乏有效查询条件")
                    # return "缺乏有效查询条件"
            except Exception as e:
                self.logger.warning(f"LLM解析失败: {e}")
                print(f"LLM解析失败: {e}")

        # 回退到规则解析
        result = self._parse_with_rules(query)
        print("\n=== 最终查询条件 (规则解析) ===")
        print(f"查询条件: {result}")
        return result

    def _parse_with_rules(self, query: str) -> QueryConditions:
        """使用规则解析查询"""
        conditions = QueryConditions()

        # 解析时间
        conditions.start_date, conditions.end_date = self._extract_time_range(query)

        # 解析应用名称
        conditions.app_names = self._extract_app_names(query)

        # 解析关键词
        conditions.keywords = self._extract_keywords(query)

        return conditions

    def _extract_time_range(
        self, query: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """提取时间范围"""
        now = datetime.now()
        start_date = None
        end_date = None

        # 检查时间关键词
        for keyword, days_ago in self.time_keywords.items():
            if keyword in query:
                if keyword in ["今天"]:
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = now
                elif keyword in ["昨天"]:
                    yesterday = now - timedelta(days=1)
                    start_date = yesterday.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = yesterday.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )
                elif keyword in ["本周"]:
                    # 本周一开始
                    days_since_monday = now.weekday()
                    start_date = (now - timedelta(days=days_since_monday)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    end_date = now
                else:
                    start_date = now - timedelta(days=days_ago)
                    end_date = now
                break

        # 检查具体日期格式（如：2024-01-01）
        date_pattern = r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})"
        dates = re.findall(date_pattern, query)
        if dates:
            try:
                date_str = dates[0].replace("/", "-")
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                start_date = parsed_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_date = parsed_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            except ValueError:
                pass

        return start_date, end_date

    def _extract_app_names(self, query: str) -> Optional[List[str]]:
        """提取应用名称"""
        friendly_app_names = []

        # 首先检查app_mapping中支持的应用名称
        for app_name in app_mapper.get_supported_apps():
            if app_name in query:
                friendly_app_names.append(app_name)

        # 检查传统的应用别名映射
        for app_alias, real_names in self.app_name_mapping.items():
            if app_alias in query and app_alias not in friendly_app_names:
                friendly_app_names.append(app_alias)

        # 直接匹配可能的应用名称
        app_patterns = [
            r"在([\u4e00-\u9fa5a-zA-Z0-9\s]+)上",  # 在XX上
            r"([\u4e00-\u9fa5a-zA-Z0-9\s]+)应用",  # XX应用
            r"([\u4e00-\u9fa5a-zA-Z0-9\s]+)软件",  # XX软件
        ]

        for pattern in app_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                app_name = match.strip()
                if app_name and app_name not in friendly_app_names:
                    friendly_app_names.append(app_name)

        # 转换为实际进程名
        if friendly_app_names:
            actual_process_names = []
            for app_name in friendly_app_names:
                process_names = app_mapper.get_process_names(app_name)
                if process_names:
                    actual_process_names.extend(process_names)
                else:
                    # 如果映射中没有找到，保留原名称
                    actual_process_names.append(app_name)
            return actual_process_names

        return None

    def _extract_keywords(self, query: str) -> Optional[List[str]]:
        """提取关键词 - 改进版本，区分功能描述词和搜索关键词"""
        keywords = []

        # 检查是否有明确的搜索意图
        search_indicators = ["搜索", "查找", "包含", "关于", "找到", "寻找"]
        has_search_intent = any(indicator in query for indicator in search_indicators)

        # 如果没有搜索意图，直接返回None
        if not has_search_intent:
            return None

        # 功能描述词列表（这些词不应该作为搜索关键词）
        function_words = [
            "聊天",
            "浏览",
            "编辑",
            "查看",
            "打开",
            "使用",
            "运行",
            "操作",
            "活动",
            "记录",
            "情况",
            "状态",
        ]

        # 停用词列表
        stop_words = [
            "帮我",
            "总结",
            "一下",
            "查找",
            "搜索",
            "显示",
            "看看",
            "的",
            "在",
            "上",
            "中",
            "里",
            "包含",
            "关于",
            "找到",
            "寻找",
        ]

        # 创建查询副本用于处理
        processed_query = query

        # 移除时间词汇
        for time_word in self.time_keywords.keys():
            processed_query = processed_query.replace(time_word, "")

        # 移除应用名称
        for app_alias in self.app_name_mapping.keys():
            processed_query = processed_query.replace(app_alias, "")

        # 分词并过滤
        words = re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", processed_query)
        for word in words:
            if word not in stop_words and word not in function_words and len(word) > 1:
                keywords.append(word)

        return keywords if keywords else None

    def _build_parsing_prompt(self, query: str) -> str:
        """构建LLM解析提示词"""
        return f"""请解析以下自然语言查询，提取出结构化的查询条件。

查询: {query}

请返回JSON格式的结果，包含以下字段：
- time_range: {{"start": "YYYY-MM-DD HH:MM:SS", "end": "YYYY-MM-DD HH:MM:SS"}} 或 null
- app_names: ["应用名称1", "应用名称2"] 或 null
- keywords: ["关键词1", "关键词2"] 或 null

常见应用名称映射：
- 微信: WeChat
- QQ: QQ
- 浏览器: Chrome, Firefox, Edge
- VS Code: Code
- Word: WINWORD
- Excel: EXCEL

时间解析规则：
- 今天: 当天0点到现在
- 昨天: 昨天全天
- 本周: 本周一到现在
- 具体日期: 如2024-01-01

只返回JSON，不要其他解释。"""

    def _build_query_conditions(self, parsed_data: Dict[str, Any]) -> QueryConditions:
        """从解析数据构建查询条件"""
        conditions = QueryConditions()

        # 处理时间范围 - 支持两种格式
        if parsed_data.get("time_range"):
            time_range = parsed_data["time_range"]
            if time_range.get("start"):
                conditions.start_date = datetime.fromisoformat(time_range["start"])
            if time_range.get("end"):
                conditions.end_date = datetime.fromisoformat(time_range["end"])
        else:
            # 处理直接的start_date和end_date字段
            if parsed_data.get("start_date"):
                try:
                    conditions.start_date = datetime.fromisoformat(
                        parsed_data["start_date"]
                    )
                except (ValueError, TypeError):
                    pass
            if parsed_data.get("end_date"):
                try:
                    conditions.end_date = datetime.fromisoformat(
                        parsed_data["end_date"]
                    )
                except (ValueError, TypeError):
                    pass

        # 处理应用名称 - 使用app_mapping转换为实际进程名
        if parsed_data.get("app_names"):
            actual_process_names = []
            for app_name in parsed_data["app_names"]:
                # 使用AppMapper获取当前平台的实际进程名
                process_names = app_mapper.get_process_names(app_name)
                if process_names:
                    actual_process_names.extend(process_names)
                else:
                    # 如果映射中没有找到，保留原名称
                    actual_process_names.append(app_name)
            conditions.app_names = (
                actual_process_names if actual_process_names else None
            )

        # 处理关键词
        if parsed_data.get("keywords"):
            conditions.keywords = parsed_data["keywords"]

        return conditions


# 创建全局实例
query_parser = QueryParser()
