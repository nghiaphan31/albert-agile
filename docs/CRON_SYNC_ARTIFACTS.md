# Cron sync_artifacts (spec III.8-O, F1 (sync_artifacts cron))

Pour activer le rapport hebdomadaire de dérive Architecture.md :

```bash
# Ajouter à la crontab (crontab -e)
0 0 * * 0 cd /home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile && source .venv/bin/activate && python scripts/sync_artifacts.py --project-id albert-agile >> logs/sync_artifacts_cron.log 2>&1
```

Dimanche minuit. Rapport dans `logs/sync_artifacts_*.log`.
