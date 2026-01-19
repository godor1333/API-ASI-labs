#!/usr/bin/env python3
"""
Запуск всех тестов проекта
"""
import unittest
import sys
import os

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 70)
    print("🧪 ЗАПУСК ТЕСТОВ ПРОЕКТА")
    print("=" * 70)
    
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Находим все тесты
    loader = unittest.TestLoader()
    
    # Тестовые модули
    test_modules = [
        'tests.test_agents',
        'tests.test_detector', 
        'tests.test_environment',
        'tests.test_integration'
    ]
    
    # Загружаем и запускаем тесты
    all_suites = []
    
    for module_name in test_modules:
        try:
            suite = loader.loadTestsFromName(module_name)
            all_suites.append(suite)
            print(f"✅ Загружены тесты: {module_name}")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить {module_name}: {e}")
    
    if not all_suites:
        print("❌ Нет тестов для запуска!")
        return False
    
    # Объединяем все сьюты
    combined_suite = unittest.TestSuite(all_suites)
    
    # Запускаем тесты
    print("\n" + "=" * 70)
    print("🚀 ЗАПУСК ТЕСТОВ...")
    print("=" * 70)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    # Статистика
    print("\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 70)
    print(f"✅ Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Провалено: {len(result.failures)}")
    print(f"⚠️ Ошибок: {len(result.errors)}")
    print(f"📈 Всего тестов: {result.testsRun}")
    
    # Сохраняем отчет
    with open("results/test_report.txt", "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ОТЧЕТ О ТЕСТИРОВАНИИ\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Всего тестов: {result.testsRun}\n")
        f.write(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}\n")
        f.write(f"Провалено: {len(result.failures)}\n")
        f.write(f"Ошибок: {len(result.errors)}\n\n")
        
        if result.failures:
            f.write("ПРОВАЛЕННЫЕ ТЕСТЫ:\n")
            for test, traceback in result.failures:
                f.write(f"\n{test}: {traceback[:200]}...\n")
        
        if result.errors:
            f.write("\nОШИБКИ:\n")
            for test, traceback in result.errors:
                f.write(f"\n{test}: {traceback[:200]}...\n")
    
    print(f"\n💾 Отчет сохранен: results/test_report.txt")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Создаем папку для результатов если нет
    os.makedirs("results", exist_ok=True)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        sys.exit(0)
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        sys.exit(1)