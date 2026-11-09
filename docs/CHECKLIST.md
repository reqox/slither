# Execution Checklist

## На старте каждой сессии
- [ ] Прочитать PROJECT_CONTEXT.md, ROADMAP.md, CHECKLIST.md, DECISIONS.md, RESULTS.md, NEW_CHAT_PROMPT.md.
- [ ] Проверить ветку, git status и последние изменения.
- [ ] Проверить задачу текущей сессии и критерии готовности.
- [ ] Не перезаписывать незакоммиченные изменения.
- [ ] Выполнять ровно одну небольшую задачу за сессию.

## Foundation
- [x] Создать основные проектные документы.
- [ ] Проверить оборудование и CUDA runtime на целевой машине.
- [ ] Настроить lint/test/CI.

## Environment MVP
- [x] Реализовать базовую игровую логику.
- [x] Реализовать Gymnasium API.
- [x] Определить observation space/action space.
- [x] Реализовать seeded reset.
- [x] Добавить базовые terminal conditions и reward shaping.
- [x] Добавить random-agent smoke test.
- [x] Проверять конечность числовых параметров среды.
- [ ] Запустить pytest и Gymnasium env checker в целевом окружении.
- [ ] Проверить поведение при столкновениях и сборе еды на граничных сценариях.

## PPO
- [x] Добавить базовую CLI-команду PPO train.
- [x] Добавить сохранение checkpoint и TensorBoard logging.
- [x] Добавить CLI-команду evaluation на фиксируемых seeds.
- [ ] Выполнить реальный train run, сохранить checkpoint и TensorBoard event logs.
- [ ] Сохранять конфиг и per-episode evaluation results.
- [ ] Сравнить с random/scripted baseline.

## Perception and browser integration (future)
- [ ] Определить визуальные объекты и формат наблюдения для реальной игры.
- [ ] Проверить качество read-only распознавания на тестовых кадрах.
- [ ] Проверить актуальные правила Slither.io и разрешённые интерфейсы расширения.
- [ ] Спроектировать явные Start/Stop controls и аварийное отключение.
- [ ] Проверить возможность автоматического ввода без обхода защит.
- [ ] Если автоматический ввод недопустим, подготовить Advisor mode.

## Перед завершением сессии
- [ ] Запустить релевантные тесты и сохранить точные команды/вывод.
- [ ] Обновить ROADMAP и CHECKLIST.
- [ ] Добавить результаты и артефакты в RESULTS.md.
- [ ] Записать новые решения в DECISIONS.md.
- [ ] Обновить NEW_CHAT_PROMPT.md одной конкретной следующей задачей.
- [ ] Указать commit SHA и рабочую ветку.
