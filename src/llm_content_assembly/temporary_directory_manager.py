import os 
import tempfile
import shutil
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

class TemporaryDirectoryManager:
    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        logger.info(f"Created Temporary Directory {self.tempdir}")
    
    def get_temp_file_path(self,filename):
        return os.path.join(self.tempdir,filename)
    
    def get_tempdir(self):
        return self.tempdir
    
    def cleanup(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
            logger.info(f"Temporary Directory {self.tempdir} deleted")
    def __del__(self):
        # Ensure cleanup is done even if the object is deleted
        self.cleanup()

def main():
    manager = TemporaryDirectoryManager()
    print(manager.get_tempdir())
if __name__ == "__main__":
    main()