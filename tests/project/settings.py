SECRET_KEY = '  '
INSTALLED_APPS = ('tests.project.app',)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}
