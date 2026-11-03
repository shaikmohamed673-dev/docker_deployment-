# Deploy this yourself — every move

Do these in **PowerShell**. Keep Docker Desktop running.

You already have Docker:

- Docker 29.8.0
- Docker Compose v5.5.1

Project folder:

```text
C:\Users\shaik\personal-docker-lab
```

---

## Move 1 — Prove Docker is alive

```powershell
docker version
docker compose version
docker ps
```

What you should see: client + server versions, and a list of running containers (maybe empty).

If the **server** part fails, start Docker Desktop and wait until it says running.

---

## Move 2 — Enter the project

```powershell
cd C:\Users\shaik\personal-docker-lab
dir
```

Read `Dockerfile` and `docker-compose.yml` before you run anything. The comments in those files are part of the lesson.

---

## Move 3 — Create your local env file

```powershell
copy .env.example .env
notepad .env
```

You can leave the defaults. `.env` is gitignored so secrets never go to GitHub.

---

## Move 4 — Build the image (without starting the app yet)

This teaches you the image vs container difference.

```powershell
docker build -t personal-task-board:local .
```

What happened:

1. Docker read `Dockerfile`
2. Pulled `python:3.12-slim` if needed
3. Installed Flask + gunicorn
4. Copied `app/`
5. Tagged the result `personal-task-board:local`

Check it:

```powershell
docker images personal-task-board
```

---

## Move 5 — Run one container by hand (optional, good for learning)

```powershell
docker run --name task-board-manual -p 8080:8000 -d personal-task-board:local
```

Meaning of the flags:

| Flag | Meaning |
|------|---------|
| `--name` | human name for this container |
| `-p 8080:8000` | your PC port 8080 → container port 8000 |
| `-d` | run in the background |

Open http://localhost:8080

Inspect:

```powershell
docker ps
docker logs task-board-manual
docker exec -it task-board-manual /bin/sh
```

Inside the shell:

```sh
ls /app
wget -qO- http://127.0.0.1:8000/health
exit
```

Stop and remove this manual container before using Compose (same port 8080):

```powershell
docker stop task-board-manual
docker rm task-board-manual
```

---

## Move 6 — The real way: Compose

Compose builds, names, ports, env, and the data volume for you.

```powershell
docker compose up --build -d
```

| Part | Meaning |
|------|---------|
| `up` | create and start services |
| `--build` | rebuild image if Dockerfile/app changed |
| `-d` | detached |

Then:

```powershell
docker compose ps
docker compose logs -f web
```

`Ctrl+C` only leaves the log stream. The container keeps running.

Health check in the browser: http://localhost:8080/health

Add a task in the UI. That writes SQLite at `/data/tasks.db` **inside** the container, which is stored in the named volume `task-data`.

---

## Move 7 — Prove persistence

```powershell
docker compose down
docker compose up -d
```

Open the app again. Your tasks should still be there.

That is the point of:

```yaml
volumes:
  - task-data:/data
```

Wipe data only when you mean it:

```powershell
docker compose down -v
```

`-v` deletes the named volume.

---

## Move 8 — Useful debug commands

```powershell
docker compose ps
docker inspect task-board --format "{{.State.Health.Status}}"
docker compose logs --tail 50 web
docker volume ls
docker compose down
```

---

## Move 9 — After practice, push to GitHub

Only after the app runs.

```powershell
cd C:\Users\shaik\personal-docker-lab
git status
git add .
git commit -m "Add Dockerized personal task board for DevOps practice"
```

On GitHub: create an empty repo (no README). Then:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/personal-docker-lab.git
git push -u origin main
```

Confirm `.env` is **not** in `git status`.

---

## Common mistakes

- **Port already in use:** change `APP_PORT` in `.env` to `8081`
- **Docker daemon not running:** start Docker Desktop
- **Old container still using 8080:** `docker ps` then `docker stop <name>`
- **Changed Python code but UI looks old:** `docker compose up --build -d`
