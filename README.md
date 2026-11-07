# Personal Task Board

A small Flask app you run in Docker. Use it as a personal DevOps lab: build an image, start a container, keep data in a volume, then push the repo to GitHub.

## What you will learn

- How a Docker **image** is built from a `Dockerfile`
- How **Compose** starts the container, maps ports, and stores data
- How `/health` proves the process inside the container is alive
- How a **named volume** keeps tasks after `docker compose down`

## Project layout

```
personal-docker-lab/
├── Dockerfile              # recipe for the image
├── docker-compose.yml      # how to run the container
├── .dockerignore           # files that must NOT go into the image
├── .gitignore              # files that must NOT go to GitHub
├── .env.example            # sample environment variables
├── requirements.txt        # Python packages
├── LEARNING-GUIDE.md       # do-this-yourself deploy steps
├── app/
│   ├── main.py             # Flask API + pages
│   ├── templates/          # HTML
│   └── static/             # CSS + JS
└── data/                   # local SQLite folder (ignored in git)
```

## Quick start (Linux)

Install Docker Engine and the Docker Compose plugin for your Linux distribution, then run these commands from the project directory:

```sh
cp .env.example .env
docker compose up --build -d
```

Open http://localhost:8080

Stop:

```sh
docker compose down
```

Data stays in the Docker volume `task-data` until you run `docker compose down -v`.

## Later: GitHub

Do not commit `.env`. Push after you have practiced the deploy steps locally.
