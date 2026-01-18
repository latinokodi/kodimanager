import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class KodiInstance:
    id: str
    name: str
    path: str
    version: str
    created_at: float  # Timestamp

    def is_valid(self) -> bool:
        return os.path.exists(self.path) and os.path.isdir(self.path)

    @property
    def executable_path(self) -> str:
        # Standard kodi path
        return os.path.join(self.path, "kodi.exe")
    
    @property
    def portable_data_path(self) -> str:
        return os.path.join(self.path, "portable_data")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
