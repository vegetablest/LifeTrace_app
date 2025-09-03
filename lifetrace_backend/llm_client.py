from openai import OpenAI
import logging
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM客户端，用于与OpenAI兼容的API进行交互"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 使用的模型名称
        """
        self.api_key = api_key or "sk-8l2Kkkjshq5tqIgKg7BOL6boFCZbXAZy0tYsWrK1m7lAEk29"
        self.base_url = base_url or "https://api.openai-proxy.org/v1"
        self.model = model or "claude-sonnet-4-20250514"
        
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            logger.info(f"LLM客户端初始化成功，使用模型: {self.model}")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """检查LLM客户端是否可用"""
        return self.client is not None
    
    def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        分类用户意图，判断是否需要数据库查询
        
        Args:
            user_query: 用户的自然语言输入
            
        Returns:
            包含意图分类结果的字典
        """
        if not self.is_available():
            logger.warning("LLM客户端不可用，使用规则分类")
            return self._rule_based_intent_classification(user_query)
        
        try:
            prompt = f"""
请分析以下用户输入，判断用户的意图类型。

用户输入："{user_query}"

请判断这个输入属于以下哪种类型：
1. "database_query" - 需要查询数据库的请求（如：搜索截图、统计使用情况、查找特定应用等）
2. "general_chat" - 一般对话（如：问候、闲聊、询问功能等）
3. "system_help" - 系统帮助请求（如：如何使用、功能说明等）

请以JSON格式返回结果：
{{
    "intent_type": "database_query/general_chat/system_help",
    "confidence": 0.0-1.0,
    "needs_database": true/false
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个智能助手，专门用于分析用户意图。请严格按照JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 打印LLM响应到控制台和日志
            print(f"\n=== LLM意图分类响应 ===")
            print(f"用户输入: {user_query}")
            print(f"LLM回复: {result_text}")
            # print(result_text)
            print(f"=== 响应结束 ===\n")
            
            logger.info(f"LLM意图分类 - 用户输入: {user_query}")
            logger.info(f"LLM意图分类 - 原始响应: {result_text}")
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown代码块标记
                clean_text = result_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                result = json.loads(clean_text)
                logger.info(f"意图分类结果: {result['intent_type']}, 置信度: {result['confidence']}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"LLM返回的不是有效JSON: {result_text}")
                return self._rule_based_intent_classification(user_query)
                
        except Exception as e:
            logger.error(f"LLM意图分类失败: {e}")
            return self._rule_based_intent_classification(user_query)
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        使用LLM解析用户查询，提取时间范围、应用名称和关键词
        
        Args:
            user_query: 用户的自然语言查询
            
        Returns:
            解析后的查询条件字典
        """
        if not self.is_available():
            logger.warning("LLM客户端不可用，使用规则解析")
            return self._rule_based_parse(user_query)
        
        # 获取当前时间作为参考
        current_time = datetime.now()
        current_date_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        system_prompt = f"""
你是一个查询解析助手。用户会提供关于历史记录的查询，你需要从中提取以下信息：

当前时间是：{current_date_str}

1. 时间范围：开始时间和结束时间（如果有的话）
2. 应用名称：用户提到的具体应用程序（如微信、QQ、浏览器等）
3. 关键词：用户想要搜索的关键内容，用数组形式返回，重点是这里应该是用户问句中的关键性名词，如果没有明确关键词可以填null
4. 查询类型：总结、搜索、统计等

请以JSON格式返回结果，包含以下字段：
{{
  "start_date": "YYYY-MM-DD HH:MM:SS" 或 null,
  "end_date": "YYYY-MM-DD HH:MM:SS" 或 null,
  "app_names": ["应用名称1", "应用名称2"] 或 null,
  "keywords": ["关键词1", "关键词2"],
  "query_type": "summary|search|statistics|other",
  "confidence": 0.0-1.0
}}

注意：
- 如果没有明确的时间信息，start_date和end_date设为null
- 如果时间是相对的（如"今天"、"昨天"、"上周"），请基于当前时间{current_date_str}转换为具体日期
- "今天"应该设置为当天的00:00:00到23:59:59
- 应用名称要标准化（如"微信"统一为"WeChat"），并以数组形式返回
- 关键词要提取核心概念
- 只需要返回json 不要返回其他任何信息
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请解析这个查询：{user_query}"}
                ],
                model=self.model,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 打印LLM响应到控制台和日志
            print(f"\n=== LLM查询解析响应 ===")
            print(f"用户查询: {user_query}")
            print(f"LLM回复: {result_text}")
            # print(result_text)
            print(f"=== 响应结束 ===\n")
            
            logger.info(f"LLM查询解析 - 用户查询: {user_query}")
            logger.info(f"LLM查询解析 - 解析结果: {result_text}")
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown代码块标记和额外文本
                clean_text = result_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                # 如果包含解释文本，尝试提取JSON部分
                if '解析说明：' in clean_text or '\n\n' in clean_text:
                    lines = clean_text.split('\n')
                    json_lines = []
                    in_json = False
                    brace_count = 0
                    
                    for line in lines:
                        if line.strip().startswith('{'):
                            in_json = True
                            brace_count += line.count('{') - line.count('}')
                            json_lines.append(line)
                        elif in_json:
                            brace_count += line.count('{') - line.count('}')
                            json_lines.append(line)
                            if brace_count <= 0:
                                break
                    
                    if json_lines:
                        clean_text = '\n'.join(json_lines)
                
                result = json.loads(clean_text)
                return result
            except json.JSONDecodeError:
                print("解析失败")
                logger.warning("LLM返回的不是有效JSON，使用规则解析")
                return self._rule_based_parse(user_query)
                
        except Exception as e:
            logger.error(f"LLM查询解析失败: {e}")
            return self._rule_based_parse(user_query)
    
    def generate_summary(self, query: str, context_data: List[Dict[str, Any]]) -> str:
        """
        基于检索到的数据生成总结
        
        Args:
            query: 用户原始查询
            context_data: 检索到的相关数据
            
        Returns:
            生成的总结文本
        """
        if not self.is_available():
            return self._fallback_summary(query, context_data)
        
        # 构建上下文
        context_text = self._build_context(context_data)
        
        system_prompt = """
你是一个智能助手，专门帮助用户分析和总结历史记录数据。

用户会提供一个查询和相关的历史数据，你需要：
1. 理解用户的查询意图
2. 分析提供的历史数据
3. 生成准确、有用的总结

请用中文回答，保持简洁明了，重点突出关键信息。
"""
        
        user_prompt = f"""
用户查询：{query}

相关历史数据：
{context_text}

请基于以上数据回答用户的查询。
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # 打印LLM响应到控制台和日志
            print(f"\n=== LLM总结生成响应 ===")
            print(f"用户查询: {query}")
            print(f"LLM回复: {result}")
            print(f"=== 响应结束 ===\n")
            
            logger.info(f"LLM总结生成 - 用户查询: {query}")
            logger.info(f"LLM总结生成 - 生成结果: {result}")
            logger.info(f"LLM生成总结成功，长度: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"LLM总结生成失败: {e}")
            return self._fallback_summary(query, context_data)
    
    def _rule_based_intent_classification(self, user_query: str) -> Dict[str, Any]:
        """基于规则的意图分类（备用方案）"""
        query_lower = user_query.lower()
        
        # 数据库查询关键词
        database_keywords = [
            '搜索', '查找', '统计', '显示', '截图', '应用', '使用情况', 
            '时间', '最近', '今天', '昨天', '本周', '上周', '本月', '上月',
            'search', 'find', 'show', 'statistics', 'screenshot', 'app', 'usage'
        ]
        
        # 一般对话关键词
        chat_keywords = [
            '你好', '谢谢', '再见', '怎么样', '如何', '为什么', '什么是',
            'hello', 'hi', 'thanks', 'bye', 'how', 'what', 'why'
        ]
        
        # 系统帮助关键词
        help_keywords = [
            '帮助', '功能', '使用方法', '教程', '说明', '介绍',
            'help', 'function', 'tutorial', 'guide', 'instruction'
        ]
        
        # 计算匹配分数
        database_score = sum(1 for keyword in database_keywords if keyword in query_lower)
        chat_score = sum(1 for keyword in chat_keywords if keyword in query_lower)
        help_score = sum(1 for keyword in help_keywords if keyword in query_lower)
        
        # 判断意图类型
        if database_score > 0:
            intent_type = "database_query"
            confidence = min(0.8, 0.5 + database_score * 0.1)
            needs_database = True
        elif help_score > 0:
            intent_type = "system_help"
            confidence = min(0.7, 0.4 + help_score * 0.1)
            needs_database = False
        elif chat_score > 0:
            intent_type = "general_chat"
            confidence = min(0.6, 0.3 + chat_score * 0.1)
            needs_database = False
        else:
            # 默认认为是数据库查询（保守策略）
            intent_type = "database_query"
            confidence = 0.3
            needs_database = True
        
        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "needs_database": needs_database
        }
    
    def _rule_based_parse(self, user_query: str) -> Dict[str, Any]:
        """基于规则的查询解析（备用方案）"""
        import re
        from datetime import datetime, timedelta
        
        result = {
            "start_date": None,
            "end_date": None,
            "app_names": None,
            "keywords": [],
            "query_type": "search",
            "confidence": 0.5
        }
        
        # 时间关键词映射
        time_keywords = {
            '今天': 0,
            '昨天': 1,
            '前天': 2,
            '本周': 7,
            '上周': 14,
            '最近一周': 7,
            '本月': 30,
            '上月': 60
        }
        
        # 检测时间范围
        now = datetime.now()
        for keyword, days_ago in time_keywords.items():
            if keyword in user_query:
                if keyword in ['本周', '上周', '最近一周']:
                    # 计算一周前
                    start_date = now - timedelta(days=days_ago)
                    result["start_date"] = start_date.isoformat()
                    result["end_date"] = now.isoformat()
                elif keyword in ['今天']:
                    # 今天
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    result["start_date"] = start_date.isoformat()
                    result["end_date"] = now.isoformat()
                elif keyword in ['昨天', '前天']:
                    # 昨天或前天
                    target_date = now - timedelta(days=days_ago)
                    start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    result["start_date"] = start_date.isoformat()
                    result["end_date"] = end_date.isoformat()
                break
        
        # 应用名称映射
        app_mapping = {
            "微信": "WeChat",
            "QQ": "QQ",
            "浏览器": "Browser",
            "chrome": "Chrome",
            "firefox": "Firefox",
            "edge": "Edge"
        }
        
        # 检测应用名称
        for chinese_name, english_name in app_mapping.items():
            if chinese_name in user_query.lower() or english_name.lower() in user_query.lower():
                result["app_names"] = [english_name]
                break
        
        # 检测查询类型
        if any(word in user_query for word in ["总结", "汇总", "概括"]):
            result["query_type"] = "summary"
        elif any(word in user_query for word in ["统计", "数量", "多少"]):
            result["query_type"] = "statistics"
        
        # 简单的关键词提取
        keywords = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', user_query)
        result["keywords"] = [kw for kw in keywords if len(kw) > 1]
        
        return result
    
    def _build_context(self, context_data: List[Dict[str, Any]]) -> str:
        """构建上下文文本"""
        if not context_data:
            return "没有找到相关的历史数据。"
        
        context_parts = []
        for i, item in enumerate(context_data[:10]):  # 限制最多10条
            timestamp = item.get('timestamp', '未知时间')
            app_name = item.get('app_name', '未知应用')
            ocr_text = item.get('ocr_text', '无文本内容')
            
            context_parts.append(f"{i+1}. 时间: {timestamp}, 应用: {app_name}\n   内容: {ocr_text[:200]}...")
        
        return "\n\n".join(context_parts)
    
    def _fallback_summary(self, query: str, context_data: List[Dict[str, Any]]) -> str:
        """备用总结方案"""
        if not context_data:
            return "抱歉，没有找到相关的历史记录数据。"
        
        summary_parts = [
            f"根据您的查询 '{query}'，我找到了 {len(context_data)} 条相关记录：",
            ""
        ]
        
        # 按应用分组
        app_groups = {}
        for item in context_data:
            app_name = item.get('app_name', '未知应用')
            if app_name not in app_groups:
                app_groups[app_name] = []
            app_groups[app_name].append(item)
        
        for app_name, items in app_groups.items():
            summary_parts.append(f"• {app_name}: {len(items)} 条记录")
        
        summary_parts.append("")
        summary_parts.append("如需更详细的分析，请提供更具体的查询条件。")
        
        return "\n".join(summary_parts)