# ShellCoach Registration App

## Initial Database Migration Instructions

Run the following commands to initialize and apply database migrations:

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

