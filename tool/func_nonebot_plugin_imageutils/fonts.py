import anyio
import httpx
import shutil
import traceback
from pathlib import Path
from PIL import ImageFont
from functools import lru_cache
from fontTools.ttLib import TTFont
from collections import namedtuple
from PIL.ImageFont import FreeTypeFont
from matplotlib.ft2font import FT2Font
from typing import List, Union, Optional, Set, Iterator
from matplotlib.font_manager import FontManager, FontProperties

from .types import *

# 从自定义模块导入字体路径
from Twip import TTF_PATH

try:
    from nonebot import get_driver
    from nonebot.log import logger
except:
    import loguru
    logger = loguru.logger

# 直接使用从 Twip 导入的 TTF_PATH
FONT_PATH = TTF_PATH

# 简化字体管理器，避免复杂的字体搜索
font_manager = FontManager()

# 全局缓存，避免重复加载
_font_cache = {}
_glyph_cache = {}

def add_font_to_manager(path: Union[str, Path]):
    """添加字体到管理器 - 简化版本"""
    try:
        if isinstance(path, Path):
            path = str(path.resolve())
        font_manager.addfont(path)
        logger.info(f"Successfully added font: {path}")
    except Exception as exc:
        logger.warning(f"Failed to add font {path}: {exc}")

# 只添加指定的字体文件
if FONT_PATH.exists():
    add_font_to_manager(FONT_PATH)
else:
    logger.error(f"Font file not found: {FONT_PATH}")

class Font:
    def __init__(self, family: str, fontpath: Path, valid_size: Optional[int] = None):
        self.family = family
        self.path = fontpath.resolve()
        self.valid_size = valid_size
        
        # 延迟加载字形表，避免初始化时立即加载所有字体
        self._glyph_table_loaded = False
        self._glyph_table: Set[int] = set()
        
        # 缓存键，用于 lru_cache
        self._cache_key = f"{self.path}_{self.valid_size}"

    def _ensure_glyph_table_loaded(self):
        """确保字形表已加载"""
        if not self._glyph_table_loaded:
            try:
                # 使用缓存避免重复解析
                cache_key = f"glyph_{self.path}"
                if cache_key in _glyph_cache:
                    self._glyph_table = _glyph_cache[cache_key]
                else:
                    # 只加载第一个字体编号，避免加载所有变体
                    ttfont = TTFont(self.path, fontNumber=0, lazy=True)
                    for table in ttfont["cmap"].tables:
                        self._glyph_table.update(table.cmap.keys())
                    ttfont.close()
                    # 缓存结果
                    _glyph_cache[cache_key] = self._glyph_table
                
                self._glyph_table_loaded = True
                logger.debug(f"Loaded glyph table for {self.family}, {len(self._glyph_table)} glyphs")
            except Exception as e:
                logger.error(f"Failed to load glyph table for {self.path}: {e}")
                # 设置空表避免重复尝试
                self._glyph_table = set()
                self._glyph_table_loaded = True

    @classmethod
    def find(
        cls,
        family: str,
        style: FontStyle = "normal",
        weight: FontWeight = "normal",
        fallback_to_default: bool = True,
    ) -> "Font":
        """查找字体 - 简化版本，只返回默认字体"""
        return cls.load_default_font()

    @classmethod
    def load_default_font(cls) -> "Font":
        """加载默认字体 - 带缓存"""
        cache_key = "default_font"
        if cache_key in _font_cache:
            return _font_cache[cache_key]
        
        if FONT_PATH.exists():
            font = cls(FONT_PATH.stem, FONT_PATH)
            _font_cache[cache_key] = font
            return font
        else:
            # 回退到系统默认字体
            logger.warning("Default font not found, using system default")
            try:
                # 使用简单的默认字体
                font = cls("system_default", Path("."))
                _font_cache[cache_key] = font
                return font
            except Exception as e:
                logger.error(f"Failed to load system default font: {e}")
                # 创建虚拟字体对象避免崩溃
                font = cls("fallback", Path("."))
                _font_cache[cache_key] = font
                return font

    @classmethod
    def find_special_font(cls, family: str) -> Optional["Font"]:
        """查找特殊字体 - 简化版本"""
        # 只在确实需要时才查找特殊字体
        SpecialFont = namedtuple("SpecialFont", ["family", "fontname", "valid_size"])
        SPECIAL_FONTS = {
            "Apple Color Emoji": SpecialFont("Apple Color Emoji", "Apple Color Emoji.ttc", 160),
            "Noto Color Emoji": SpecialFont("Noto Color Emoji", "NotoColorEmoji.ttf", 109),
        }

        if family in SPECIAL_FONTS:
            cache_key = f"special_{family}"
            if cache_key in _font_cache:
                return _font_cache[cache_key]
            
            prop = SPECIAL_FONTS[family]
            fontname = prop.fontname
            
            # 检查字体文件是否存在
            possible_paths = [
                FONT_PATH.parent / fontname,
                Path("/System/Library/Fonts") / fontname,  # macOS
                Path("/usr/share/fonts") / fontname,       # Linux
                Path("C:/Windows/Fonts") / fontname,       # Windows
            ]
            
            for fontpath in possible_paths:
                if fontpath.exists():
                    font = cls(prop.family, fontpath, prop.valid_size)
                    _font_cache[cache_key] = font
                    return font
            
            # 尝试通过系统查找
            try:
                system_font = ImageFont.truetype(fontname, prop.valid_size)
                fontpath = Path(str(system_font.path))
                font = cls(prop.family, fontpath, prop.valid_size)
                _font_cache[cache_key] = font
                return font
            except OSError:
                logger.debug(f"Special font {family} not found")
        
        return None

    def load_font(self, fontsize: int) -> FreeTypeFont:
        """以指定大小加载字体 - 带缓存和资源限制"""
        cache_key = f"pil_font_{self.path}_{fontsize}"
        
        if cache_key in _font_cache:
            return _font_cache[cache_key]
        
        try:
            if self.valid_size:
                # 使用固定大小
                font = ImageFont.truetype(str(self.path), self.valid_size, encoding="utf-8")
            else:
                font = ImageFont.truetype(str(self.path), fontsize, encoding="utf-8")
            
            _font_cache[cache_key] = font
            return font
        except Exception as e:
            logger.error(f"Failed to load font {self.path} at size {fontsize}: {e}")
            # 返回默认字体避免崩溃
            return ImageFont.load_default()

    def has_char(self, char: str) -> bool:
        """检查字体是否支持某个字符 - 延迟加载"""
        self._ensure_glyph_table_loaded()
        return ord(char) in self._glyph_table

# 简化回退字体逻辑
default_fallback_fonts = [FONT_PATH.stem] if FONT_PATH.exists() else ["system_default"]

def get_proper_font(
    char: str,
    style: FontStyle = "normal",
    weight: FontWeight = "normal",
    fontname: Optional[str] = None,
    fallback_fonts: List[str] = [],
) -> Font:
    """
    获取合适的字体 - 简化版本
    
    :参数:
        * ``char``: 字符
        * ``style``: 字体样式，默认为 "normal"
        * ``weight``: 字体粗细，默认为 "normal"
        * ``fontname``: 忽略此参数
        * ``fallback_fonts``: 忽略此参数
    """
    # 直接返回默认字体，避免复杂的查找逻辑
    default_font = Font.load_default_font()
    
    # 只有在确实需要检查特殊字符时才进行复杂操作
    try:
        char_code = ord(char)
        # 如果是emoji或特殊字符范围，尝试特殊字体
        if char_code > 0xFFFF or (0x1F600 <= char_code <= 0x1F64F):  # emoji范围
            special_font = Font.find_special_font("Apple Color Emoji") or Font.find_special_font("Noto Color Emoji")
            if special_font:
                return special_font
    except:
        pass
    
    return default_font

async def add_font(fontname: str, source: Union[str, Path]):
    """添加字体 - 禁用此功能"""
    logger.info("Font addition is disabled in simplified font system")

async def download_font(url: str, fontpath: Path):
    """下载字体 - 禁用此功能"""
    logger.info("Font download is disabled in simplified font system")

def clear_font_cache():
    """清理字体缓存，用于内存管理"""
    global _font_cache, _glyph_cache
    _font_cache.clear()
    _glyph_cache.clear()
    logger.info("Font cache cleared")