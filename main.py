import argparse  
import logging  
import asyncio  
from config.config_loader import ConfigLoader  
from parsers.http_parser import HTTPParser
from parsers.curl_parser import CurlParser  
from requesters.async_requester import AsyncHTTPRequester  
from utils.logger import setup_logger 
import json

def main() -> None:  
    parser = argparse.ArgumentParser(description='模块化HTTP请求工具')  
    parser.add_argument('-c', '--config', required=True, help='配置文件路径')  
    parser.add_argument('-p', '--proxy', help='代理地址')  
    parser.add_argument('-v', action='store_true', help='日志详细输出')
    parser.add_argument('-o', '--out', default='http_requests.log', help='日志文件')
    parser.add_argument('--headers', default=None, help='请求头替换')
    args = parser.parse_args()  

    logging_level = logging.DEBUG if args.v else logging.INFO  
    logger = setup_logger(level=logging_level, log_file=args.out)

    try:  
        config_loader = ConfigLoader(logger)  
        config = config_loader.load_config(args.config)  

        http_parser = HTTPParser(logger)  
        curl_parser = CurlParser(logger)  
        headers = None
        if args.headers:
            with open(args.headers, 'r', encoding='utf-8') as file:  
                headers = json.load(file) 
        requester = AsyncHTTPRequester(proxy=args.proxy, logger=logger, headers=headers)  

        all_requests = {  
            key: http_parser.parse_http_file(filepath, key) if filepath.endswith(".http") else  
                 curl_parser.parse_curl_file(filepath, key)  
            for key, filepath in config['r_files'].items()  
        }  

        async def execute_requests() -> None:  
            tasks = []  
            for test_config in config['r_config']:  
                request_keys = test_config['http_details'].split(',')  
                http_details = [all_requests[key] for key in request_keys]  

                for _ in range(test_config.get('thread', 1)):  
                    task = asyncio.create_task(  
                        requester.send_multiple_requests(  
                            http_details,  
                            test_config.get('count', 1),  
                            test_config.get('inner_interval', 0)  
                        )  
                    )  
                    tasks.append(task)  

            await asyncio.gather(*tasks)  

        asyncio.run(execute_requests())  
        logger.info(f"完成 {len(all_requests)} 组请求")  

    except Exception as e:  
        logger.error(f"执行过程中发生错误: {e}")  
        logger.error(e.with_traceback())

if __name__ == '__main__':  
    main()