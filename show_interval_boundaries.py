import time
from datetime import datetime, timezone

UTC_TAI_OFFSET=27
INTERVAL_SIZE_SECONDS = 2**23 / 1000.0
INTERVAL_MASK = 0xFFFFFFFFFFFFFFFF & ~(2**23 - 1)

now = time.time()
interval_start = \
    (int((now + UTC_TAI_OFFSET) * 1000) & INTERVAL_MASK) / 1000.0

for i in [-2, -1, 0, 1, 2]:
    t = datetime.fromtimestamp(interval_start + i*INTERVAL_SIZE_SECONDS,
                               timezone.utc)
    prefix = '>' if i==0 else ' '
    print(f'{prefix} {t.isoformat()}')
