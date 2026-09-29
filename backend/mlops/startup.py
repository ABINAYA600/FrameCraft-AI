from __future__ import annotations

import threading
import time

from .config import (
    MONITOR_INTERVAL_SECONDS
)

from .service import (
    snapshot_and_monitor
)


_started = False

_lock = threading.Lock()


def start_background_monitor():

    global _started


    with _lock:

        if _started:

            return

        _started = True


    def worker():

        # Give FastAPI time to finish startup.
        time.sleep(10)


        while True:

            try:

                snapshot_and_monitor()

            except Exception as error:

                print(
                    "[MLOps] "
                    f"monitor error: {error}"
                )


            time.sleep(
                max(
                    60,
                    MONITOR_INTERVAL_SECONDS
                )
            )


    thread = threading.Thread(

        target=worker,

        name=
            "framecraft-mlops-monitor",

        daemon=True

    )


    thread.start()