module.exports = {
  apps: [
    {
      name: 'aims-backend',
      script: 'bash',
      args: '-c "source venv/bin/activate && PYTHONPATH=. uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --workers 4"',
      cwd: '/root/AIMS',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production',
      },
    },
    {
      name: 'aims-frontend',
      script: 'bash',
      args: '-c "cd apps/frontend && pnpm start"',
      cwd: '/root/AIMS',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: '3000',
      },
    },
  ],
};
