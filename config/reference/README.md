# Configs de référence IDE (Roo Code, Continue)

Ces fichiers sont des copies de référence des configurations Roo Code et Continue, à garder synchronisées avec les fichiers réels.

| Fichier de référence | Fichier réel | Emplacement |
|----------------------|--------------|-------------|
| `roo-code-settings.json` | `~/.config/roo-code-settings.json` | Calypso |
| `continue-config.yaml` | `C:\Users\<user>\.continue\config.yaml` | PC Windows |

## Synchronisation

### Roo Code (depuis Calypso)

```bash
# Réel → dépôt (après modification dans Roo Code)
cp ~/.config/roo-code-settings.json config/reference/roo-code-settings.json

# Dépôt → réel (restaurer ou appliquer la référence)
cp config/reference/roo-code-settings.json ~/.config/roo-code-settings.json
# Puis recharger VS Code (F1 → Reload Window) pour que Roo importe le fichier
```

### Continue (depuis le PC Windows)

Continue lit sa config sur le **client Windows**, pas sur Calypso.

- **Réel → dépôt** : copier manuellement `C:\Users\<user>\.continue\config.yaml` vers `config/reference/continue-config.yaml`
- **Dépôt → réel** : copier `config/reference/continue-config.yaml` vers `C:\Users\<user>\.continue\config.yaml`

### Script de sync (Roo uniquement, sur Calypso)

```bash
./scripts/sync_ide_configs.sh to-repo   # Réel → dépôt
./scripts/sync_ide_configs.sh to-real   # Dépôt → réel
```
