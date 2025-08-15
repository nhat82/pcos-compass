from enum import Enum

class EventType(Enum): 
    PERIOD = "Period"
    OVULATION = "Ovulation"
    SPOTTING = "Spotting"
    NOTE = "Note"
    
class FlowType(Enum): 
    LIGHT = "Light" 
    MEDIUM = "Medium"
    HEAVY = "Heavy"
