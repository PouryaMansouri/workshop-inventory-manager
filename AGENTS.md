# Production server access

- Host: `93.118.146.89`
- SSH port: `4422`
- SSH user: `administrator`
- Production app: `https://93.118.146.89:8443/`
- Application directory: `/opt/workshop`
- Backups: `/opt/workshop-backups`; run `sudo /opt/workshop/deploy/backup.sh` before database migrations.
- The server application directory is a file deployment, not a Git checkout. Preserve `.env`, `media/`, `staticfiles/`, and `logs/` when updating it.
- The SSH and sudo password is stored only on this workstation in `.agent-ssh.env` (mode `0600`). This file is excluded from Git and Docker builds. Never print or commit the password.
