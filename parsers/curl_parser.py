from typing import Dict, Any  
import logging  
import re  

class CurlParser:  
    def __init__(self, logger: logging.Logger = None) -> None:  
        self.logger = logger or logging.getLogger(__name__)  

    def parse_curl_file(self, filepath: str, tag: str = 'default') -> Dict[str, Any]:  
        try:  
            with open(filepath, 'r', encoding='utf-8') as file:  
                curl_command = file.read().strip()  

            parsed_request = self._parse_curl_command(curl_command)  
            http_detail = {  
                "method": parsed_request['method'],  
                "url": parsed_request['url'],  
                "headers": parsed_request.get('headers', {}),  
                "body": parsed_request.get('body'),  
                "tag": tag  
            }  

            self.logger.info(f"成功解析Curl请求: {tag}")  
            return http_detail  
        except Exception as e:  
            self.logger.error(f"Curl文件解析错误: {e}")  
            raise  

    def _parse_curl_command(self, curl_command: str) -> Dict[str, Any]:  
        curl_command = curl_command.replace('\\n', ' ').strip()  
        url_match = re.search(r'[\'"]?(https?://[^\s]+)[\'"]?', curl_command)  
        if not url_match:  
            raise ValueError("无法提取URL")  
        url = url_match.group(1)
        # 修复边界情况：分离引号和实际URL  
        url_segments = url.split("'", 1) if "'" in url else url.split('"', 1)  
        url = url_segments[0].strip("'\"")  # 去除残留引号 

        method = self._extract_method(curl_command)  
        headers = self._extract_headers(curl_command)  
        body = self._extract_body(curl_command)  

        return {  
            'method': method,  
            'url': url,  
            'headers': headers,  
            'body': body  
        }  

    def _extract_method(self, curl_command: str) -> str:  
        method_map = {  
            '-X POST': 'POST',  
            '-X PUT': 'PUT',  
            '-X DELETE': 'DELETE',  
            '-X PATCH': 'PATCH',  
            '-X HEAD': 'HEAD',  
            '-X OPTIONS': 'OPTIONS'  
        }  

        for method_flag, method in method_map.items():  
            if method_flag in curl_command:  
                return method  
        return 'GET'  # 默认为GET方法  

    def _extract_headers(self, curl_command: str) -> Dict[str, str]:  
        headers = {}  
        header_matches = re.findall(r'-H\s*[\'"]([^\'"]+)[\'"]', curl_command)  

        for header in header_matches:  
            try:  
                key, value = header.split(':', 1)  
                headers[key.strip()] = value.strip()  
            except ValueError:  
                self.logger.warning(f"无法解析请求头: {header}")  

        return headers  

    def _extract_body(self, curl_command: str) -> str:  
        body_matches = re.findall(r'--data|-d\s*[\'"]([^\'"]+)[\'"]', curl_command)  
        if body_matches:  
            return body_matches[-1]  
        return None