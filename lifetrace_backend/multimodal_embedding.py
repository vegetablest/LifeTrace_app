"""
多模态嵌入模块
支持图像和文本的联合嵌入生成
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image

# 添加项目根目录到Python路径，以便直接运行此文件
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

try:
    import clip
    import torch
    from transformers import CLIPModel, CLIPProcessor

    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logging.warning(
        "多模态依赖未安装，请运行: pip install torch transformers clip-by-openai"
    )

from lifetrace_backend.config import config


class MultimodalEmbedding:
    """多模态嵌入生成器

    使用CLIP模型同时处理图像和文本，生成在同一向量空间的嵌入
    """

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """初始化多模态嵌入器

        Args:
            model_name: CLIP模型名称
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        self.clip_model = None

        # 配置参数
        self.image_embedding_dim = 512  # CLIP图像嵌入维度
        self.text_embedding_dim = 512  # CLIP文本嵌入维度
        self.max_image_size = (224, 224)  # CLIP输入图像尺寸

        self.logger = logging.getLogger(__name__)

        if MULTIMODAL_AVAILABLE:
            self._initialize_models()
        else:
            self.logger.warning("多模态功能不可用，缺少必要依赖")

    def _initialize_models(self):
        """初始化CLIP模型"""
        try:
            self.logger.info(f"正在加载CLIP模型: {self.model_name}")

            # 使用Transformers版本的CLIP
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)

            # 移动到设备
            self.model.to(self.device)
            self.model.eval()

            # 也尝试加载原版CLIP作为备选
            try:
                self.clip_model, _ = clip.load("ViT-B/32", device=self.device)
                self.logger.info("原版CLIP模型加载成功")
            except Exception as e:
                self.logger.warning(f"原版CLIP模型加载失败: {e}")

            self.logger.info(f"CLIP模型初始化完成，使用设备: {self.device}")

        except Exception as e:
            self.logger.error(f"CLIP模型初始化失败: {e}")
            self.model = None
            self.processor = None

    def is_available(self) -> bool:
        """检查多模态功能是否可用"""
        return MULTIMODAL_AVAILABLE and self.model is not None

    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """编码文本为向量

        Args:
            text: 输入文本

        Returns:
            文本嵌入向量
        """
        if not self.is_available() or not text or not text.strip():
            return None

        try:
            with torch.no_grad():
                # 使用Transformers CLIP
                inputs = self.processor(
                    text=[text], return_tensors="pt", padding=True, truncation=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                text_features = self.model.get_text_features(**inputs)
                text_features = text_features / text_features.norm(
                    dim=-1, keepdim=True
                )  # 归一化

                return text_features.cpu().numpy().flatten()

        except Exception as e:
            self.logger.error(f"文本编码失败: {e}")
            return None

    def encode_image(self, image_path: str) -> Optional[np.ndarray]:
        """编码图像为向量

        Args:
            image_path: 图像文件路径

        Returns:
            图像嵌入向量
        """
        if not self.is_available() or not os.path.exists(image_path):
            return None

        try:
            # 加载和预处理图像
            image = Image.open(image_path).convert("RGB")

            with torch.no_grad():
                # 使用Transformers CLIP
                inputs = self.processor(images=image, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                image_features = self.model.get_image_features(**inputs)
                image_features = image_features / image_features.norm(
                    dim=-1, keepdim=True
                )  # 归一化

                return image_features.cpu().numpy().flatten()

        except Exception as e:
            self.logger.error(f"图像编码失败 {image_path}: {e}")
            return None

    def encode_image_from_array(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        """从numpy数组编码图像

        Args:
            image_array: 图像数组

        Returns:
            图像嵌入向量
        """
        if not self.is_available():
            return None

        try:
            # 转换为PIL图像
            if image_array.dtype != np.uint8:
                image_array = (image_array * 255).astype(np.uint8)

            image = Image.fromarray(image_array).convert("RGB")

            with torch.no_grad():
                inputs = self.processor(images=image, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                image_features = self.model.get_image_features(**inputs)
                image_features = image_features / image_features.norm(
                    dim=-1, keepdim=True
                )

                return image_features.cpu().numpy().flatten()

        except Exception as e:
            self.logger.error(f"图像数组编码失败: {e}")
            return None

    def compute_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """计算两个嵌入向量的相似度

        Args:
            embedding1: 第一个嵌入向量
            embedding2: 第二个嵌入向量

        Returns:
            余弦相似度分数 (0-1)
        """
        try:
            # 归一化
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2

            # 余弦相似度
            similarity = np.dot(embedding1_norm, embedding2_norm)

            # 转换到0-1范围
            return float((similarity + 1) / 2)

        except Exception as e:
            self.logger.error(f"相似度计算失败: {e}")
            return 0.0

    def batch_encode_texts(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """批量编码文本

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        if not self.is_available():
            return [None] * len(texts)

        try:
            # 过滤空文本
            valid_texts = [
                (i, text) for i, text in enumerate(texts) if text and text.strip()
            ]

            if not valid_texts:
                return [None] * len(texts)

            indices, clean_texts = zip(*valid_texts)

            with torch.no_grad():
                inputs = self.processor(
                    text=clean_texts, return_tensors="pt", padding=True, truncation=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                text_features = self.model.get_text_features(**inputs)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

                features_np = text_features.cpu().numpy()

            # 构建结果列表
            results = [None] * len(texts)
            for i, idx in enumerate(indices):
                results[idx] = features_np[i]

            return results

        except Exception as e:
            self.logger.error(f"批量文本编码失败: {e}")
            return [None] * len(texts)

    def batch_encode_images(self, image_paths: List[str]) -> List[Optional[np.ndarray]]:
        """批量编码图像

        Args:
            image_paths: 图像路径列表

        Returns:
            嵌入向量列表
        """
        if not self.is_available():
            return [None] * len(image_paths)

        try:
            # 加载有效图像
            valid_images = []
            indices = []

            for i, path in enumerate(image_paths):
                if os.path.exists(path):
                    try:
                        image = Image.open(path).convert("RGB")
                        valid_images.append(image)
                        indices.append(i)
                    except Exception as e:
                        self.logger.warning(f"加载图像失败 {path}: {e}")

            if not valid_images:
                return [None] * len(image_paths)

            with torch.no_grad():
                inputs = self.processor(images=valid_images, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                image_features = self.model.get_image_features(**inputs)
                image_features = image_features / image_features.norm(
                    dim=-1, keepdim=True
                )

                features_np = image_features.cpu().numpy()

            # 构建结果列表
            results = [None] * len(image_paths)
            for i, idx in enumerate(indices):
                results[idx] = features_np[i]

            return results

        except Exception as e:
            self.logger.error(f"批量图像编码失败: {e}")
            return [None] * len(image_paths)

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "available": self.is_available(),
            "model_name": self.model_name,
            "device": self.device,
            "image_embedding_dim": self.image_embedding_dim,
            "text_embedding_dim": self.text_embedding_dim,
            "max_image_size": self.max_image_size,
        }


# 全局多模态嵌入器实例
_multimodal_embedding = None


def get_multimodal_embedding() -> MultimodalEmbedding:
    """获取全局多模态嵌入器实例"""
    global _multimodal_embedding
    if _multimodal_embedding is None:
        _multimodal_embedding = MultimodalEmbedding()
    return _multimodal_embedding


def create_multimodal_embedding(model_name: str = None) -> MultimodalEmbedding:
    """创建多模态嵌入器实例"""
    if model_name is None:
        model_name = config.get("multimodal.model_name", "openai/clip-vit-base-patch32")

    return MultimodalEmbedding(model_name)
