# Deploy this yourself — every move

Follow these steps in a **Linux terminal**. Docker Desktop is not required; install Docker Engine and the Docker Compose plugin for your distribution first.

Open a terminal in the project folder. To find the current folder:

```text
pwd
```

---

## Move 1 — Prove Docker is alive

```sh
docker version
docker compose version
docker ps
```

What you should see: client + server versions, and a list of running containers (maybe empty).

If the server part fails, check that the Docker service is running. On systemd-based distributions:

```sh
sudo systemctl status docker
sudo systemctl start docker
```

If you see a permission error, either run Docker commands with `sudo` or configure your Linux user for Docker access according to Docker's documentation.

---

## Move 2 — Enter the project

```sh
cd /path/to/docker_deployment-
ls -la
```

Read `Dockerfile` and `docker-compose.yml` before you run anything. The comments in those files are part of the lesson.

---

## Move 3 — Create your local env file

```sh
cp .env.example .env
nano .env
```

You can leave the defaults for local practice. `.env` is gitignored, so it will not be added to Git by default. Replace the sample `SECRET_KEY` before using this app beyond local practice.

---

## Move 4 — Build the image (without starting the app yet)

This teaches you the image vs container difference.

```sh
docker build -t personal-task-board:local .
```

What happened:

1. Docker read `Dockerfile`
2. Pulled `python:3.12-slim` if needed
3. Installed Flask + gunicorn
4. Copied `app/`
5. Tagged the result `personal-task-board:local`

Check it:

```sh
docker images personal-task-board
```

---

## Move 5 — Run one container by hand (optional, good for learning)

```sh
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

```sh
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

```sh
docker stop task-board-manual
docker rm task-board-manual
```

---

## Move 6 — The real way: Compose

Compose builds, names, ports, env, and the data volume for you.

```sh
docker compose up --build -d
```

| Part | Meaning |
|------|---------|
| `up` | create and start services |
| `--build` | rebuild image if Dockerfile/app changed |
| `-d` | detached |

Then:

```sh
docker compose ps
docker compose logs -f web
```

`Ctrl+C` only leaves the log stream. The container keeps running.

Health check in the browser: http://localhost:8080/health

Add a task in the UI. That writes SQLite at `/data/tasks.db` **inside** the container, which is stored in the named volume `task-data`.

---

## Move 7 — Prove persistence

```sh
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

```sh
docker compose down -v
```

`-v` deletes the named volume.

---

## Move 8 — Useful debug commands

```sh
docker compose ps
docker inspect task-board --format '{{.State.Health.Status}}'
docker compose logs --tail 50 web
docker volume ls
docker compose down
```

---

## Move 9 — After practice, push to GitHub

Only after the app runs.

```sh
cd /path/to/docker_deployment-
git status
git add .
git commit -m "Add Dockerized personal task board for DevOps practice"
```

On GitHub: create an empty repo (no README). Then:

```sh
git remote add origin https://github.com/YOUR_USERNAME/personal-docker-lab.git
git push -u origin main
```

Confirm `.env` is **not** in `git status`.

---

## Common mistakes

- **Port already in use:** change `APP_PORT` in `.env` to `8081`
- **Docker daemon not running:** start the Docker service (for example, `sudo systemctl start docker` on systemd-based distributions)
- **Old container still using 8080:** `docker ps` then `docker stop <name>`
- **Changed Python code but UI looks old:** `docker compose up --build -d`
