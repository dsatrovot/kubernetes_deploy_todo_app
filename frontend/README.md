# Taskflow React frontend

React + TypeScript + Vite, адаптивный русскоязычный интерфейс для Todo API.

## Запуск

1. Запусти FastAPI backend из предыдущего проекта на `http://localhost:8000`.
2. Установи Node.js 20+.
3. В каталоге frontend:

   ```bash
   npm install
   npm run dev
   ```

4. Открой `http://localhost:5173`.

Vite проксирует `/api` на backend `http://localhost:8000`, поэтому для локальной разработки обычно не нужен CORS.

## Production build

```bash
npm run build
```

Готовые статические файлы будут в `dist/`. Их можно отдавать через Nginx; настрой reverse proxy `/api/` на FastAPI Service.

## API contract

Используются `GET /api/todos`, `POST /api/todos`, `PATCH /api/todos/{id}`, `DELETE /api/todos/{id}`. Модель ожидает `id`, `title`, `description`, `completed`, опционально `created_at`. Если в `backend/main.py` или `schemas.py` исходного проекта пути/поля отличаются, обнови `src/api.ts`.

## Docker image

Build the frontend/Nginx image from this directory:

```bash
docker build -t todo-frontend:1.0 .
```

The Dockerfile runs `npm install` because this project archive does not include a lockfile. For repeatable production builds, run `npm install` locally, commit the generated `package-lock.json`, then change the Dockerfile to use `COPY package*.json ./` and `RUN npm ci`.

For Kubernetes, mount your Nginx ConfigMap at `/etc/nginx/conf.d/default.conf` to configure SPA fallback and proxy `/api/` to the FastAPI Service.
