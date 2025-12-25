# План дослідження: Резервне копіювання та Disaster Recovery

## Ціль дослідження

Дослідити сучасні стратегії резервного копіювання та disaster recovery для корпоративних систем, забезпечення безперервності бізнесу та захисту даних.

## Основні завдання

### 1. Стратегії резервного копіювання

- Дослідити принцип 3-2-1 для backup
- Google Vault для email та документів
- Cloud backup (AWS, Azure, Google Cloud)
- Локальне и хмарне сховища

### 2. Disaster Recovery Planning (DRP)

- RPO (Recovery Point Objective)
- RTO (Recovery Time Objective)
- Тестування DRP
- Документація процесів відновлення

### 3. Інструменти та рішення

- Google Vault та Google Cloud Backup
- Veeam для enterprise backup
- AWS Backup та Azure Backup
- Open-source рішення (Restic, Bacula)

### 4. Automation та API

- Резервне копіювання через API
- Автоматизація процесів backup
- Моніторинг та alerty
- Log management та versioning

## Ключові концепції

### RPO vs RTO
- **RPO**: Максимальна кількість даних, які можна втратити
- **RTO**: Максимальний час простою до відновлення

### Vrste Backup
- **Full Backup**: Полне копіювання всіх даних
- **Incremental**: Копіювання тільки змін
- **Differential**: Копіювання змін від останнього full backup

## Результат

Комплексний план для впровадження стратегії backup та disaster recovery.
