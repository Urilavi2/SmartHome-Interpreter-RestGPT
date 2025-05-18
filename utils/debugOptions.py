from utils.singleton import Singleton

class DebugOptions(Singleton):
    def __init__(self, debug_Level="off"):
        if hasattr(self, '_initialized') and self._initialized:
            return  # Prevent re-initialization
        level_map = {
            "high": 2,
            "low": 1,
            "off":0
        }
        self.debug_Level = debug_Level.lower()

        if self.debug_Level in level_map:
            self.debug_Level = level_map[self.debug_Level]
        else:
            raise ValueError("Invalid debug level. Choose 'high', 'low', or 'off'.")
        
        if self.debug_Level > 0:
            print(f"Debug level set to {debug_Level}.")
        self._initialized = True

    def set_debug_level(self, level):
        level_map = {
            "high": 2,
            "low": 1,
            "off": 0
        }
        if level in level_map:
            self.debug_Level = level_map[level]
        else:
            raise ValueError("Invalid debug level. Choose 'high', 'low', or 'off'.")
        
        if self.debug_Level > 0:
            print(f"Debug level set to {level}.")

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, int):
            return self.debug_Level == other
        elif isinstance(other, DebugOptions):
            return self.debug_Level == other.debug_Level
        return False
    
    def __lt__(self, other):
        if isinstance(other, str):
            return self.debug_Level < other
        elif isinstance(other, int):
            return self.debug_Level < other
        elif isinstance(other, DebugOptions):
            return self.debug_Level < other.debug_Level
        return False
    
    def __le__(self, other):
        if isinstance(other, str):
            return self.debug_Level <= other
        elif isinstance(other, int):
            return self.debug_Level <= other
        elif isinstance(other, DebugOptions):
            return self.debug_Level <= other.debug_Level
        return False
    
    def __gt__(self, other):
        if isinstance(other, str):
            return self.debug_Level > other
        elif isinstance(other, int):
            return self.debug_Level > other
        elif isinstance(other, DebugOptions):
            return self.debug_Level > other.debug_Level
        return False
    
    def __ge__(self, other):
        if isinstance(other, str):
            return self.debug_Level >= other
        elif isinstance(other, int):
            return self.debug_Level >= other
        elif isinstance(other, DebugOptions):
            return self.debug_Level >= other.debug_Level
        return False
    
    def __str__(self):
        level_map = {
            2: "high",
            1: "low",
            0: "off"
        }
        return level_map.get(self.debug_Level, "off")
    