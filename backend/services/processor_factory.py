from services.ocr_parser import SlipParser
from services.vlm_pipeline import LocalVLMPipeline
import os

class ProcessorFactory:
    """Returns the right pipeline based on PROCESSING_MODE."""
    
    _instances = {}
    
    @classmethod
    def get(cls, mode: str = None):
        if mode is None:
            mode = os.getenv("PROCESSING_MODE", "lite")
            
        if mode not in cls._instances:
            if mode == "local":
                cls._instances[mode] = LocalVLMPipeline()
            else:
                cls._instances[mode] = SlipParser()  # default: lite
                
        return cls._instances[mode]
