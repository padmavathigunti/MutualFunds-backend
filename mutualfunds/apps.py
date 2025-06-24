from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MutualfundsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mutualfunds'

    def ready(self):
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            import json

            # Create or get the interval
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.HOURS
            )

            task_name = 'Update NAVs and Portfolios Every Hour'

            # Only create if task with same name doesn't exist
            if not PeriodicTask.objects.filter(name=task_name).exists():
                PeriodicTask.objects.create(
                    interval=schedule,
                    name=task_name,
                    task='mutualfunds.tasks.update_nav_and_portfolio',  # Make sure this path is correct
                    args=json.dumps([])
                )

        except (OperationalError, ProgrammingError):
            # Avoid DB access during migrations
            pass
