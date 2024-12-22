import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from abc import ABC, abstractmethod

class ResultPointCallback(ABC):
    @abstractmethod
    def found_possible_result_point(self, point):
        """
        This method should be implemented by any class that wants to handle found result points.
        :param point: A ResultPoint instance
        """
        pass

