import logging
import time

logger = logging.getLogger('timer')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(levelname)s TIMER - %(message)s'))
logger.addHandler(stream_handler)


class Timer:
    """A context manager that measures the amount of time its context takes to execute.

    Example usage:

    with Timer('my_timer'):
        <do some work>

    When the context manager exits, it will log approximately how long in microseconds the contained
    context took to execute.
    """
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.stop_time = None

    def __enter__(self):
        self.start_time = time.monotonic_ns()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.stop_time = time.monotonic_ns()

        logger.info(f'{self.name}: {(self.stop_time - self.start_time) / 1000.0} us')
