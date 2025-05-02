#!/usr/bin/python3

from abc import ABC, abstractmethod
from typing import Tuple

class InvestmentData(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def filter_and_summarize(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        pass
    
