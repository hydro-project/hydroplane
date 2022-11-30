import datetime
import logging
from typing import Optional

from pydantic import BaseModel, Field

from ..runtimes.runtime import Runtime

logger = logging.getLogger('process_culler')


class Settings(BaseModel):
    max_age_minutes: int = Field(
        description='the maximum number of minutes that a process should be allowed to run'
    )
    culling_interval_minutes: Optional[int] = Field(
        description='the frequency, in minutes, with which the process culler runs',
        default=1
    )


class ProcessCuller:
    """A simple utility for stopping old processes.

    If enabled, the process culler is invoked once per minute, but only actually culls old processes
    at an interval determined by its `culling_interval_minutes` field. The culler will stop any
    process whose `created` field is prior to now - `max_age_minutes`.
    """
    def __init__(
            self,
            runtime: Runtime,
            max_age_minutes: int,
            culling_interval_minutes: int
    ):
        self.runtime = runtime
        self.max_age = datetime.timedelta(minutes=max_age_minutes)
        self.culling_interval = datetime.timedelta(minutes=culling_interval_minutes)
        self.last_culling: datetime.datetime = None

    def info(self) -> str:
        return f"Culling processes older than {self.max_age} every {self.culling_interval}"

    def cull_old_processes(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        if self.last_culling is None:
            next_culling = now
        else:
            next_culling = self.last_culling + self.culling_interval

        if now < next_culling:
            logger.debug(f'Skipping old process culling; next culling will occur at {next_culling}')
            return

        logger.info('Culling old processes')
        processes = self.runtime.list_processes(group=None)

        for process_info in processes:
            process_name = process_info.process_name
            process_creation_time = process_info.created
            if now - process_creation_time > self.max_age:
                logger.info(
                    f"Process '{process_name}' is older than the maximum allowed "
                    f"age of {self.max_age} (it was created at {process_creation_time}); "
                    "stopping it"
                )
                self.runtime.stop_process(process_name)

        self.last_culling = now
