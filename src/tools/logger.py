from datetime import datetime

class Logger:
    def __init__(self, filename: str, log_to_console: bool = False) -> None:
        self.filename = filename
        self.log_to_console = log_to_console
    
    def __call__(self, text: str, error: bool = False, warning: bool = False, important: bool = False) -> None:
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]{' !WARNING!' if warning else ''}{' !ERROR!' if error else ''}{' !IMPORTANT!' if important else ''} - {text}\n")
        if self.log_to_console:
            print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]{' !WARNING!' if warning else ''}{' !ERROR!' if error else ''}{' !IMPORTANT!' if important else ''} - {text}")
    def info(self, text: str):
        self.__call__(text)
    
    def warning(self, text: str):
        self.__call__(text, warning=True)
    
    def error(self, text: str):
        self.__call__(text, error=True)

    def important(self, text: str):
        self.__call__(text, important=True)