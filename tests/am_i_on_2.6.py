import sys

major, minor, _, _, _ = sys.version_info
if major==2 and minor==6:
    exit(1)
else:
    exit(0)