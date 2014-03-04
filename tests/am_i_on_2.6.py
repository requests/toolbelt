import sys

major, minor, _, _, _ = sys.version_info
if major == 2 and minor ==6:
    exit(0)
else:
    exit(1)