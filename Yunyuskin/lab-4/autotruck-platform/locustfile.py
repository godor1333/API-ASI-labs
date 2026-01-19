import uuid
from locust import HttpUser, task, between


class LogisticsLoadTest(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Вызывается один раз при создании каждого виртуального игрока"""
        # Генерируем уникальный ID для этого конкретного "бота"
        self.player_id = f"bot_{uuid.uuid4().hex[:8]}"

    @task(3)
    def view_map(self):
        self.client.get("/init_data")

    @task(1)
    def calculate_route(self):
        self.client.get(f"/calculate_route?load=10")

    @task(2)
    def check_balance(self):
        # Теперь каждый бот запрашивает СВОЙ баланс
        self.client.get(f"/get_balance/{self.player_id}")

    @task(1)
    def run_audit(self):
        # Имитация завершения рейса (создаст файл в папке players)
        payload = {
            "load": 10,
            "segments": [{"u": "A", "v": "B", "mode": "truck"}]
        }
        self.client.post(f"/audit/{self.player_id}", json=payload)