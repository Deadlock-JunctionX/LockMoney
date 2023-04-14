from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any


class BackgroundJobExecutor:
    def __init__(self) -> None:
        self.__pool = ThreadPoolExecutor(max_workers=4)

    def submit_job(self, fn, args: List[Any], kwargs: Dict[str, Any]):
        self.__pool.submit(fn, *args, **kwargs)
