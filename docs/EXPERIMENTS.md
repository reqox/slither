# Experiment Protocol

Каждый эксперимент получает уникальный ID и сохраняет:
- git commit SHA;
- полный config и seed;
- Python/PyTorch/Gymnasium/Stable-Baselines3 versions;
- CUDA availability/device name;
- total timesteps и wall-clock duration;
- TensorBoard logs;
- checkpoint;
- evaluation seeds и результаты по каждому эпизоду;
- сравнение с текущим best checkpoint.

## Evaluation rules
1. Train и evaluation seeds не пересекаются.
2. Сравнивать модели на одном и том же evaluation-наборе.
3. Записывать mean, median и standard deviation.
4. Не повышать модель до best только из-за роста training reward.
5. При недостаточной выборке обозначать результат как предварительный.
6. Любое изменение reward function требует новой baseline-оценки.

## Naming
`runs/<experiment_id>/config.json`
`runs/<experiment_id>/events.out.tfevents.*`
`checkpoints/<experiment_id>/`
`results/<experiment_id>.json`
