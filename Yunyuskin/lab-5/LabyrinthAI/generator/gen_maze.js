const labyrinthos = require('labyrinthos');

try {
    const width = 11;
    const height = 11;

    // 1. Ищем конструктор (пытаемся достать его из разных мест экспорта)
    let MazeClass;
    if (typeof labyrinthos.Maze === 'function') {
        MazeClass = labyrinthos.Maze;
    } else if (labyrinthos.default && typeof labyrinthos.default.Maze === 'function') {
        MazeClass = labyrinthos.default.Maze;
    } else if (typeof labyrinthos === 'function') {
        MazeClass = labyrinthos;
    } else {
        // Если ничего не помогло, попробуем TileMap (в новых версиях это база)
        MazeClass = labyrinthos.TileMap || (labyrinthos.default && labyrinthos.default.TileMap);
    }

    if (!MazeClass) {
        throw new Error("Библиотека Labyrinthos загружена, но конструктор Maze или TileMap не найден. Попробуйте переустановить: npm install labyrinthos@latest");
    }

    // 2. Инициализация карты
    let map = new MazeClass(width, height);

    // Заполняем всё стенами (1)
    for (let i = 0; i < map.data.length; i++) map.data[i] = 1;

    // 3. Генерация лабиринта
    const mazes = labyrinthos.mazes || (labyrinthos.default && labyrinthos.default.mazes);
    if (mazes && mazes.RecursiveBacktrack) {
        mazes.RecursiveBacktrack(map);
    } else {
        // Запасной вариант вызова алгоритма
        labyrinthos.RecursiveBacktrack(map);
    }

    // 4. Расстановка лавы (2) в тупиках
    for (let i = 0; i < map.data.length; i++) {
        if (map.data[i] === 0) {
            let x = i % width;
            let y = Math.floor(i / width);

            if ((x === 1 && y === 1) || (x === width - 2 && y === height - 2)) continue;

            let walls = 0;
            // Проверка соседей
            if (map.data[i - 1] === 1) walls++;
            if (map.data[i + 1] === 1) walls++;
            if (map.data[i - width] === 1) walls++;
            if (map.data[i + width] === 1) walls++;

            // Если 3 стены — ставим лаву
            if (walls >= 3 && Math.random() < 0.75) {
                map.data[i] = 2;
            }
        }
    }

    // 5. Вывод JSON для Python
    process.stdout.write(JSON.stringify({
        width: map.width,
        height: map.height,
        data: Array.from(map.data) // Гарантируем массив
    }));

} catch (err) {
    process.stderr.write("JS_ERROR: " + err.message);
    process.exit(1);
}