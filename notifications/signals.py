from django.dispatch import Signal


notify = Signal(providing_args=[
    'actor', 'verb', 'action_object', 'target', 'description',
    'timestamp', 'level', 'users', 'groups'
])
