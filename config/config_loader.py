import json  
import logging  
from typing import Dict, Any  

class ConfigLoader:  
    def __init__(self, logger: logging.Logger = None) -> None:  
        self.logger = logger or logging.getLogger(__name__)  

    def load_config(self, config_path: str) -> Dict[str, Any]:  
        """加载并验证配置文件"""  
        try:  
            with open(config_path, 'r', encoding='utf-8') as file:  
                config = json.load(file)  
            self._validate_config(config)  
            if config.get('desc'):  
                self.logger.info(f"配置描述: {config['desc']}")  
            return config  
        except json.JSONDecodeError as e:  
            self.logger.error(f"JSON解析错误: {e}")  
            raise  
        except FileNotFoundError:  
            self.logger.error(f"配置文件未找到: {config_path}")  
            raise  

    def _validate_config(self, config: Dict[str, Any]) -> None:  
        """验证配置文件的基本结构"""  
        required_keys = ['r_files', 'r_config']  
        for key in required_keys:  
            if key not in config:  
                raise ValueError(f"配置缺少必需的键: {key}")