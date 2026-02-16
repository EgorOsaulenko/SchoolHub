from django.apps import AppConfig

class TaskmanagerConfig(AppConfig):
    name = 'TaskManager'

    def ready(self):
        from django.template.defaultfilters import register, floatformat
        # Fix for TemplateSyntaxError: Invalid filter: 'floatform'
        # Registers 'floatform' as an alias for 'floatformat' globally.
        register.filter('floatform', floatformat)
