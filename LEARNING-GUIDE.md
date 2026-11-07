# Deploy this yourself — every move

Follow these steps in a **Linux terminal**. Docker Desktop is not required. The installation steps below are for Ubuntu and Debian; for other distributions, use the [official Docker Engine installation guide](https://docs.docker.com/engine/install/).

Open a terminal in the project folder. To find the current folder:

```text
pwd
```

---

## Move 1 — Install Docker Engine and Compose

Docker Compose is installed as the Compose plugin, so you can use it with `docker compose`.

### Ubuntu

Add Docker's official package repository and install Docker Engine, the CLI, and the Compose plugin:

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Debian

Add Docker's official package repository and install Docker Engine, the CLI, and the Compose plugin:

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

On other distributions, follow Docker's instructions for your package manager and install both **Docker Engine** and the **Docker Compose plugin**.

---

## Move 2 — Prove Docker is alive

```sh
sudo docker version
sudo docker compose version
sudo docker ps
```

What you should see: client + server versions, and a list of running containers (maybe empty).

If Docker is not running on a systemd-based distribution:

```sh
sudo systemctl status docker
sudo systemctl start docker
```

Use `sudo` before Docker commands if your user does not have permission. For optional non-root access, follow Docker's [Linux post-installation instructions](https://docs.docker.com/engine/install/linux-postinstall/); membership in the `docker` group grants root-level privileges.

---

## Move 3 — Enter the project

If you used `sudo` to run the Docker checks above, prepend `sudo` to the Docker commands in the remaining steps as well.

```sh
cd /path/to/docker_deployment-
ls -la
```

Read `Dockerfile` and `docker-compose.yml` before you run anything. The comments in those files are part of the lesson.

---

## Move 4 — Create your local env file

```sh
cp .env.example .env
nano .env
```

You can leave the defaults for local practice. `.env` is gitignored, so it will not be added to Git by default. Replace the sample `SECRET_KEY` before using this app beyond local practice.

---

## Move 5 — Build the image (without starting the app yet)

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

## Move 6 — Run one container by hand (optional, good for learning)

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

## Move 7 — The real way: Compose

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

## Move 8 — Prove persistence

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

## Move 9 — Useful debug commands

```sh
docker compose ps
docker inspect task-board --format '{{.State.Health.Status}}'
docker compose logs --tail 50 web
docker volume ls
docker compose down
```

---

## Move 10 — After practice, push to GitHub

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
