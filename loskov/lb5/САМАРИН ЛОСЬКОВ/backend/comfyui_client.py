"""
Клиент для взаимодействия с ComfyUI через WebSocket API
"""

import json
import uuid
import websocket
import threading
import queue
import time
import requests
from typing import Dict, Any, Optional, Callable
import os


class ComfyUIClient:
    """Клиент для работы с ComfyUI API"""
    
    def __init__(self, host: str = "localhost", port: int = 8188):
        """
        Инициализация клиента ComfyUI
        
        Args:
            host: Хост ComfyUI сервера
            port: Порт ComfyUI сервера
        """
        self.host = host
        self.port = port
        self.ws_url = f"ws://{host}:{port}/ws?clientId={uuid.uuid4()}"
        self.api_url = f"http://{host}:{port}"
        self.ws = None
        self.message_queue = queue.Queue()
        self.is_connected = False
        self._lock = threading.Lock()
        
    def connect(self):
        """Подключение к ComfyUI WebSocket"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Запускаем WebSocket в отдельном потоке
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Ждём подключения
            time.sleep(1)
            self.is_connected = True
            print(f"Подключено к ComfyUI на {self.ws_url}")
            
        except Exception as e:
            print(f"Ошибка подключения к ComfyUI: {e}")
            self.is_connected = False
    
    def _on_message(self, ws, message):
        """Обработка сообщений от ComfyUI"""
        if isinstance(message, str):
            try:
                data = json.loads(message)
                self.message_queue.put(data)
            except json.JSONDecodeError:
                # Если это не JSON, пробуем обработать как текст
                if "invalid prompt" in message.lower() or "does not exist" in message.lower():
                    error_data = {
                        "type": "invalid_prompt",
                        "message": {"message": message, "details": message}
                    }
                    self.message_queue.put(error_data)
    
    def _on_error(self, ws, error):
        """Обработка ошибок WebSocket"""
        print(f"WebSocket ошибка: {error}")
        self.is_connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Обработка закрытия соединения"""
        print("WebSocket соединение закрыто")
        self.is_connected = False
    
    def queue_prompt(self, prompt: Dict[str, Any]) -> str:
        """
        Отправка промпта в очередь ComfyUI
        
        Args:
            prompt: Словарь с workflow для ComfyUI
            
        Returns:
            prompt_id: ID промпта в очереди
            
        Raises:
            ValueError: Если ноды не найдены или другие ошибки
        """
        if not self.is_connected:
            self.connect()
        
        prompt_id = str(uuid.uuid4())
        data = {
            "prompt": prompt,
            "client_id": str(uuid.uuid4())
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/prompt",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Проверяем на ошибки в ответе
            if "error" in result:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                if "does not exist" in error_msg:
                    raise ValueError(f"Нода не найдена в ComfyUI: {error_msg}. "
                                   f"Установите необходимые custom nodes для SVD.")
                raise ValueError(f"Ошибка ComfyUI: {error_msg}")
            
            return result.get("prompt_id", prompt_id)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к ComfyUI: {e}")
            raise ValueError(f"Не удалось подключиться к ComfyUI: {e}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            print(f"Ошибка отправки промпта: {e}")
            raise ValueError(f"Ошибка отправки промпта: {e}")
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """
        Получение изображения из ComfyUI
        
        Args:
            filename: Имя файла
            subfolder: Подпапка
            folder_type: Тип папки (output, input, temp)
            
        Returns:
            bytes: Данные изображения
        """
        try:
            data = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            response = requests.get(
                f"{self.api_url}/view",
                params=data
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Ошибка получения изображения: {e}")
            raise
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Ожидание завершения обработки промпта
        
        Args:
            prompt_id: ID промпта
            timeout: Таймаут в секундах
            
        Returns:
            dict: Результаты обработки
            
        Raises:
            ValueError: Если произошла ошибка выполнения
        """
        start_time = time.time()
        results = {}
        
        while time.time() - start_time < timeout:
            try:
                message = self.message_queue.get(timeout=1)
                
                # Проверяем на ошибки
                if message.get("type") == "invalid_prompt":
                    error_data = message.get("message", {})
                    error_msg = error_data.get("message", "Unknown error") if isinstance(error_data, dict) else str(error_data)
                    raise ValueError(f"Неверный промпт: {error_msg}")
                
                if message.get("type") == "execution_error":
                    error_data = message.get("data", {})
                    error_msg = error_data.get("error", {}).get("message", "Unknown error") if isinstance(error_data, dict) else str(error_data)
                    raise ValueError(f"Ошибка выполнения: {error_msg}")
                
                if message.get("type") == "execution_cached":
                    prompt_id_msg = message.get("data", {}).get("prompt_id")
                    if prompt_id_msg == prompt_id:
                        continue
                
                if message.get("type") == "executing":
                    data = message.get("data", {})
                    if data.get("node") is None and data.get("prompt_id") == prompt_id:
                        # Выполнение завершено
                        break
                
                if message.get("type") == "progress":
                    data = message.get("data", {})
                    print(f"Прогресс: {data.get('value', 0)}/{data.get('max', 100)}")
                
                if message.get("type") == "executed":
                    data = message.get("data", {})
                    if data.get("prompt_id") == prompt_id:
                        results = data.get("output", {})
                        break
                        
            except queue.Empty:
                continue
        
        return results
    
    def generate_svd_workflow(
        self,
        image_path: str,
        num_frames: int = 25,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        motion_bucket_id: int = 127
    ) -> Dict[str, Any]:
        """
        Генерация workflow для Stable Video Diffusion
        
        Args:
            image_path: Путь к входному изображению
            num_frames: Количество кадров
            num_inference_steps: Количество шагов инференса
            guidance_scale: Guidance scale
            motion_bucket_id: Motion bucket ID
            
        Returns:
            dict: Workflow для ComfyUI
        """
        # Базовый workflow для SVD
        # Примечание: это упрощённый пример, реальный workflow зависит от установленных нод ComfyUI
        workflow = {
            "1": {
                "inputs": {
                    "image": image_path,
                    "num_frames": num_frames,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "motion_bucket_id": motion_bucket_id
                },
                "class_type": "StableVideoDiffusionLoader"
            }
        }
        
        return workflow
    
    def close(self):
        """Закрытие соединения"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
