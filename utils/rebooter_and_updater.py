import time
import os
from datetime import datetime

from utils.database.drop_databases import drop_amount_of_requests, drop_daily_users
from utils.paths.get_env_python_path import get_env_pip_command


def update_g4f_package_and_make_daily_reboot(wait_for: int) -> None:
    while True:
        time.sleep(wait_for)
        current_time = datetime.today().strftime('%H:%M')
        if current_time == '00:00':
            drop_daily_users()
            drop_amount_of_requests()
            os.system(f"{get_env_pip_command()} install -U g4f")
