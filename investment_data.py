#!/usr/bin/python3

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

import cache

class InvestmentData(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        pass

    @abstractmethod
    def flush_cache(self):
        pass

    @abstractmethod
    def cache(self) -> cache.FuncCache | None:
        return None
    
    @abstractmethod
    def set_cache(self, c: Dict[Any, Any]) -> None:
        pass

    @abstractmethod
    def enable_cache(self) -> None:
        pass

    @abstractmethod
    def set_progress_period(self, p: int) -> None:
        pass
