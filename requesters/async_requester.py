import asyncio  
import aiohttp  
import logging
import shortuuid  
from typing import List, Dict, Any  

class AsyncHTTPRequester:  
    def __init__(self, proxy: str = None, logger: logging.Logger = None, headers: Dict[str, str] = None) -> None:  
        self.proxy = proxy  
        self.logger = logger or logging.getLogger(__name__)  
        self.headers = headers

    async def send_request(self, session: aiohttp.ClientSession,  
                            method: str, url: str,  
                            headers: Dict[str, str],  
                            body: Any, tag: str,  
                            interval: float = 0) -> Dict[str, Any]:  
        try:
            if self.headers:
                for key in self.headers.keys():
                    headers[key] = self.headers[key]
            
            if not url.startswith(('http://', 'https://')):  
                url = 'https://' + headers.get('Host', '') + url  

            if interval > 0:  
                await asyncio.sleep(interval)  

            tag = tag + '_' + shortuuid.uuid()
            
            self.logger.info(f'发送请求: {tag}, 方法: {method}, URL: {url}')  
            self.logger.debug(f'发送请求头: {headers}, 发送请求体: {body}')

            request_methods = {  
                'GET': session.get,  
                'POST': session.post,  
                'PUT': session.put,  
                'DELETE': session.delete  
            }  

            method_func = request_methods.get(method.upper())  
            if not method_func:  
                raise ValueError(f"不支持的HTTP方法: {method}")  

            async with method_func(url, headers=headers, data=body, proxy=self.proxy) as response:  
                resp_text = await response.text()  
                resp_status = response.status  

                self.logger.info(f"tag: {tag} 响应状态: {resp_status}, 响应内容长度: {len(resp_text)}")  
                self.logger.debug(f"tag: {tag} resp: {resp_text}")  

                return {"status": resp_status, "text": resp_text}  

        except aiohttp.ClientError as e:  
            self.logger.error(f'网络请求错误: {e}')  
            raise  
        except Exception as e:  
            self.logger.error(f'请求处理错误: {e}')  
            raise  

    async def send_multiple_requests(self, http_details: List[Dict[str, Any]],  
                                      multiple: int = 1, inner_interval: float = 0) -> List[Dict[str, Any]]:  

        async with aiohttp.ClientSession() as session:  
            tasks = []  
            for _ in range(multiple):
                for i in range(len(http_details)):
                    http_detail = http_details[i]
                    task = asyncio.create_task(  
                        self.send_request(  
                            session,  
                            http_detail['method'],  
                            http_detail['url'],  
                            http_detail['headers'],  
                            http_detail['body'],  
                            http_detail['tag'],  
                            inner_interval * i  
                        )  
                )  
                tasks.append(task)  

            responses = await asyncio.gather(*tasks)  
            return responses