from apscheduler.schedulers.background import BackgroundScheduler


class BirthdayReminderScheduler:
    def __init__(self, autostart):

        # Create a background scheduler
        self.scheduler = BackgroundScheduler()

        # Start scheduler
        if autostart:
            self.start()

    def start(self):
        self.scheduler.start()

    def add_job(self, func: any, hours: int):
        self.scheduler.add_job(
            func, 'interval', hours=hours)
