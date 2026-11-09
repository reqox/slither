# Execution Checklist

## На старте каждой сессии
- [ ] Прочитать PROJECT_CONTEXT.md, ROADMAP.md, CHECKLIST.md, DECISIONS.md, RESULTS.md, NEW_CHAT_PROMPT.md.
- [ ] Проверить ветку, git status и последние изменения.
- [ ] Проверить issue/задачу текущего этапа и критерии готовности.
- [ ] Не перезаписывать незакоммиченные изменения.

## Foundation
- [x] Создать основные проектные документы.
- [ ] Проверить оборудование и CUDA runtime на целевой машине.
- [ ] Настроить lint/test/CI.

## Environment MVP
- [ ] Реализовать игровую логику.
- [ ] Реализовать Gymnasium API.
- [ ] Проверить observation space/action space.
- [ ] Проверить детерминизм одинаковых seed.
- [ ] Проверить terminal conditions и reward.
- [ ] Запустить random-agent smoke test.

## PPO
- [ ] Обучить baseline.
- [ ] Сохранить checkpoint и конфиг.
- [ ] Получить TensorBoard event logs.
- [ ] Провести evaluation на фиксированных seeds.
- [ ] Сравнить с random/scripted baseline.

## Перед завершением сессии
- [ ] Запустить релевантные тесты и сохранить точные команды/вывод.
- [ ] Обновить ROADMAP и CHECKLIST.
- [ ] Добавить результаты и артефакты в RESULTS.md.
- [ ] Записать решения в DECISIONS.md.
- [ ] Обновить NEW_CHAT_PROMPT.md конкретной следующей задачей.
- [ ] Указать commit SHA и рабочую ветку.
