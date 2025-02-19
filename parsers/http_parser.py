from email import parser, policy  
from typing import Any, Dict, Tuple  
import logging  

class HTTPParser:  
    def __init__(self, logger: logging.Logger = None) -> None:  
        self.logger = logger or logging.getLogger(__name__)  
        self.parser = parser.Parser(policy=policy.HTTP)  

    def parse_http_file(self, filepath: str, tag: str = 'default') -> Dict[str, Any]:  
        try:  
            with open(filepath, 'r', encoding='utf-8') as file:  
                request = file.read()  

            start_line, headers, body = self._parse_http_package(request)  
            http_detail = {  
                "method": start_line.split()[0],  
                "url": start_line.split()[1],  
                "headers": headers,  
                "body": body,  
                "tag": tag  
            }  
            self.logger.info(f"成功解析HTTP请求: {tag}")  
            return http_detail  
        except Exception as e:  
            self.logger.error(f"HTTP文件解析错误: {e}")  
            raise  

    def _parse_http_package(self, http_pkg: str) -> Tuple[str, Dict[str, str], Any]:  
        separators = ['\n', '\r\n']  
        for sep in separators:  
            try:  
                return self._split_http_package(sep, http_pkg)  
            except Exception:  
                continue  
        raise ValueError("无法解析HTTP数据包")  

    def _split_http_package(self, separator: str, http_pkg: str) -> Tuple[str, Dict[str, str], Any]:  
        tmp = http_pkg.split(sep=separator, maxsplit=1)  
        start_line = tmp[0]  
        others = tmp[1]  

        msg = self.parser.parsestr(text=others, headersonly=False)  
        headers = {k: str(v) for k, v in msg.items()}  
        body = msg.get_payload()  

        return start_line, headers, body