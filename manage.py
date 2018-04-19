#!/usr/bin/env python
import os
from toolkit.cmdline import cmdline

if __name__ == "__main__":
    # 将 "proj.settings" 改为cmdline.settings，注意没有引号
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", cmdline.settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # 修改 sys.argv 为 cmdline.command
    execute_from_command_line(cmdline.command)
