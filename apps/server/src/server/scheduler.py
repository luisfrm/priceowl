import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from .app import create_app
from .config import settings
from .jobs.daily_check import daily_price_check

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def run_job_with_context(app, job_func):
    """
    Decorator/wrapper to run a job within the Flask application context.
    This ensures SQLAlchemy and Flask extensions are properly configured.
    """
    def wrapper():
        logger.info(f"Starting job: {job_func.__name__}")
        try:
            with app.app_context():
                job_func()
            logger.info(f"Successfully completed job: {job_func.__name__}")
        except Exception as e:
            logger.error(f"Error executing job {job_func.__name__}: {e}", exc_info=True)
    return wrapper


def main() -> None:
    app = create_app()
    scheduler = BlockingScheduler()

    wrapped_job = run_job_with_context(app, daily_price_check)

    scheduler.add_job(
        func=wrapped_job,
        trigger="cron",
        hour=settings.DAILY_CHECK_HOUR,
        minute=settings.DAILY_CHECK_MINUTE,
        id="daily_price_check",
        replace_existing=True,
    )

    logger.info(
        f"Scheduler configured to run 'daily_price_check' at "
        f"{settings.DAILY_CHECK_HOUR:02d}:{settings.DAILY_CHECK_MINUTE:02d} everyday."
    )
    logger.info("Starting BlockingScheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutdown requested. Exiting.")


if __name__ == "__main__":
    main()
