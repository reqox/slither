# Roadmap

Статусы: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`. Обновлять по фактическому состоянию.

## Phase 0 — Foundation
- [x] Зафиксировать миссию, границы и архитектурные принципы.
- [x] Создать документацию для передачи между сессиями.
- [ ] Проверить доступность GPU/PyTorch в целевом окружении.
- [ ] Зафиксировать воспроизводимую среду разработки и CI.

## Phase 1 — Local environment MVP
- [ ] Реализовать Gymnasium-совместимую среду: reset/step/observation/reward/termination.
- [ ] Добавить детерминированные seeds и unit tests правил.
- [ ] Добавить smoke test случайного агента.
- [ ] Добавить базовую отрисовку Pygame и режим headless.

## Phase 2 — PPO baseline
- [ ] Реализовать обучение PPO на локальной среде.
- [ ] Добавить TensorBoard, checkpoints и конфиг эксперимента.
- [ ] Добавить evaluation на фиксированном наборе seeds.
- [ ] Ввести best-checkpoint promotion только при статистически осмысленном улучшении.

## Phase 3 — Environment quality
- [ ] Улучшить геометрию и физику, сверить с выбранными игровыми правилами.
- [ ] Добавить управляемых scripted opponents.
- [ ] Добавить curriculum и domain randomization.
- [ ] Проверить перенос стратегии на ранее не встречавшиеся seeds.

## Phase 4 — Strategic agent
- [ ] Исследовать frame stacking / recurrent PPO.
- [ ] Добавить прогноз траекторий и опасностей.
- [ ] Добавить тактики охоты и оценки риска.
- [ ] Добавить tournament evaluation против разных классов оппонентов.

## Phase 5 — Human-facing tools
- [ ] Read-only vision pipeline для изображения официальной игры.
- [ ] Advisor: рекомендации человеку без автоматического управления клиентом.
- [ ] Dashboard: эпизоды, метрики, сравнение checkpoints.

## Phase 6 — Research loop
- [ ] Автоматизация серии экспериментов.
- [ ] Автоматическое сравнение кандидатов с baseline.
- [ ] Promotion/rollback по заранее заданным критериям.
- [ ] Отчёты о регрессиях и обобщающей способности.

## Definition of Done для каждой фазы
- Код и конфиги находятся в репозитории.
- Тесты и smoke/evaluation пройдены; результаты записаны в RESULTS.md.
- CHECKLIST и ROADMAP отражают фактическое состояние.
- DECISIONS содержит новые архитектурные решения и их причины.
- NEW_CHAT_PROMPT содержит точную задачу следующей сессии.
