def test_accuracy_consistency(global_model, test_dataset):
    print("\n[ACCURACY] Проверка стабильности...")
    accuracies = []
    y_true = [d['label'] for d in test_dataset]

    for i in range(3):
        y_pred = [global_model.predict(d['input']).argmax(1).item() for d in test_dataset]
        metrics = global_model.get_metrics(y_true, y_pred)
        accuracies.append(metrics['accuracy'])
        print(f"Прогон {i+1}: Accuracy = {metrics['accuracy']}")

    assert len(set(accuracies)) == 1
    print(f"✅ УСПЕХ: Точность стабильна ({accuracies[0]})")