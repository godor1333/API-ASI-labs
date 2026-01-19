def calculate_integrity_test(load, capacity):
    # Упрощенная логика из твоего main.py
    overloads = 1 if load > capacity else 0
    integrity = max(0, 100 - (overloads * 45))
    return integrity

def test_truck_overload():
    # Тест: Грузовик (10т), везем 15т. Должно быть 55% целостности.
    result = calculate_integrity_test(15, 10)
    assert result == 55
    print("Test Overload: PASSED")

def test_truck_normal():
    # Тест: Грузовик (10т), везем 5т. Должно быть 100%.
    result = calculate_integrity_test(5, 10)
    assert result == 100
    print("Test Normal: PASSED")

if __name__ == "__main__":
    test_truck_overload()
    test_truck_normal()