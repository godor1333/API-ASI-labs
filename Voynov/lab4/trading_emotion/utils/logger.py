import logging
from pathlib import Path
from datetime import datetime
import sys

class GameLogger:
    """Логирование игрового процесса"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Настраиваем логирование с учетом кодировки Windows
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"game_{timestamp}.log"
        
        # Используем UTF-8 для файлового хендлера
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Stream handler для консоли (без эмодзи для Windows)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Форматирование без эмодзи для Windows
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Форматирование для консоли без эмодзи
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Настраиваем логгер
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Убираем эмодзи из сообщений для Windows
        self.use_emojis = sys.platform != 'win32'
        
        if self.use_emojis:
            self.logger.info("🚀 Инициализация логгера игры")
        else:
            self.logger.info("Инициализация логгера игры")
    
    def _clean_message(self, message):
        """Очистка эмодзи для Windows"""
        if self.use_emojis:
            return message
        
        # Убираем эмодзи (Unicode символы)
        import re
        # Убираем основные эмодзи
        emoji_pattern = re.compile("["
            "\U0001F600-\U0001F64F"  # эмоции
            "\U0001F300-\U0001F5FF"  # символы и пиктограммы
            "\U0001F680-\U0001F6FF"  # транспорт и карты
            "\U0001F700-\U0001F77F"  # алхимия
            "\U0001F780-\U0001F7FF"  # геометрические фигуры
            "\U0001F800-\U0001F8FF"  # дополнительные стрелки
            "\U0001F900-\U0001F9FF"  # дополнительные символы
            "\U0001FA00-\U0001FA6F"  # шахматы
            "\U00002600-\U000026FF"  # разные символы
            "\U00002700-\U000027BF"  # Dingbats
            "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub('', message)
    
    def log_episode_start(self, episode_num, epsilon=None):
        """Логирование начала эпизода"""
        if epsilon is not None:
            message = f"Начало эпизода {episode_num} (ε={epsilon:.3f})"
        else:
            message = f"Начало эпизода {episode_num}"
        
        self.logger.info(self._clean_message(message))
    
    def log_step(self, episode, step, action, reward, total_reward, objects_detected):
        """Логирование шага"""
        message = (f"Эпизод {episode}, Шаг {step}: "
                   f"Действие={action}, Награда={reward:+.1f}, "
                   f"Всего={total_reward:.1f}, Объектов={objects_detected}")
        self.logger.debug(self._clean_message(message))
    
    def log_episode_end(self, episode_num, total_reward, steps, epsilon=None):
        """Логирование конца эпизода"""
        if epsilon is not None:
            message = (f"Конец эпизода {episode_num}: "
                      f"Шагов={steps}, Награда={total_reward:.1f}, "
                      f"Следующий ε={epsilon:.3f}")
        else:
            message = (f"Конец эпизода {episode_num}: "
                      f"Шагов={steps}, Награда={total_reward:.1f}")
        
        self.logger.info(self._clean_message(message))
    
    def log_training_start(self, params):
        """Логирование начала обучения"""
        self.logger.info(self._clean_message("Начало обучения RL-агента"))
        self.logger.info(f"Параметры: {params}")
    
    def log_training_end(self, summary):
        """Логирование конца обучения"""
        self.logger.info(self._clean_message("Обучение завершено"))
        self.logger.info(f"Итоги: {summary}")
    
    def log_detection_info(self, objects_count, frame_info=None):
        """Логирование информации о детекции"""
        if frame_info:
            message = f"Обнаружено {objects_count} объектов: {frame_info}"
        else:
            message = f"Обнаружено {objects_count} объектов"
        
        self.logger.debug(self._clean_message(message))