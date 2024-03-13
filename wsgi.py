from src.server import app
from src.tools.config_parser import Config

if __name__ == "__main__":
    cfg = Config('config.json')
    app.run(cfg.host, cfg.port, cfg.debug)