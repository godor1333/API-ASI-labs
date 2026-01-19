"""
Backend модуль для генерации видео через Stable Video Diffusion
"""

from .video_generator import VideoGenerator
from .comfyui_client import ComfyUIClient
from .keyframe_generator import KeyframeGenerator

__all__ = ['VideoGenerator', 'ComfyUIClient', 'KeyframeGenerator']
