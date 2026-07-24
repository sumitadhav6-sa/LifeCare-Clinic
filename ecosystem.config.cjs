module.exports = {
  apps: [{
    name: 'bajrang-clinic',
    script: 'python',
    args: '-m gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 wsgi:application',
    cwd: '/home/user/webapp',
    env: { PYTHONPATH: '/home/user/webapp', FLASK_ENV: 'development' },
    watch: false,
    instances: 1,
    exec_mode: 'fork'
  }]
};
