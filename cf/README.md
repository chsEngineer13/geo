# cloud foundry deployment
Environment variables are stored and passed to the app from the manifest.yml

```yaml
 env:
```

## initial push
```bash
cf push -c "bash cf/init_db.sh"
```

__Note:__ this will run the init_db.sh and sync the django database

## additional pushes
```bash
cf push
```
