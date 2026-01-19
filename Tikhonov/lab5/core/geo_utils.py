import re
import os


class GeoFinder:
    def __init__(self, streets_file=None):
        if streets_file is None:
            # Путь относительно корня проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            streets_file = os.path.join(base_dir, 'data', 'streets.txt')

        self.streets = []
        try:
            if os.path.exists(streets_file):
                with open(streets_file, 'r', encoding='utf-8') as f:
                    self.streets = [line.strip() for line in f.readlines() if line.strip()]
                print(f"📖 Загружено {len(self.streets)} названий улиц.")
            else:
                print(f"⚠️ Файл {streets_file} не найден!")
        except Exception as e:
            print(f"❌ Ошибка загрузки словаря: {e}")

    def find_locations(self, text):
        if not text:
            return []

        found = []
        clean_text = text.lower()
        for street in self.streets:
            # Поиск целого слова (чтобы 'Мира' не находилось в 'Пирамида')
            pattern = rf'\b{re.escape(street.lower())}\b'
            if re.search(pattern, clean_text):
                found.append(street)

        return list(set(found))