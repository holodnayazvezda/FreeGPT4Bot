import time
import os
from datetime import datetime


def update_g4f_package(wait_for: int) -> None:
    while True:
        time.sleep(wait_for)
        current_time = datetime.today().strftime('%H:%M')
        if current_time == '00:00':
            os.system(".\.venv\Scripts\pip.exe install -U g4f")
