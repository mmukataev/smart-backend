module.exports = {
  apps: [
    {
      name: "smart-apa-backend",
      script: "./venv/bin/gunicorn",
      args: "smart_apa_project.wsgi:application --bind 0.0.0.0:8000",
      cwd: "/var/opt/smart_apa_project",
      env: {
        DJANGO_SETTINGS_MODULE: "smart_apa_project.settings",
        PYTHONUNBUFFERED: "1"
      },
      interpreter: "none"
    }
  ]
}
