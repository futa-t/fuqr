from dataclasses import dataclass


@dataclass
class BBox:
    top: int = 0
    left: int = 0
    width: int = 0
    height: int = 0
