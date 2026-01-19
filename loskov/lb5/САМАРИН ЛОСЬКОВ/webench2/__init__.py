"""
Webench2 модуль для оценки качества видео
"""

from .evaluator import Webench2Evaluator
from .metrics import MetricsCalculator
from .benchmark import run_regression_benchmark, compare_models

__all__ = ['Webench2Evaluator', 'MetricsCalculator', 'run_regression_benchmark', 'compare_models']
