from parsers.http_parser import HTTPParser, CurlParser

http_parser = HTTPParser()

curl_parser = CurlParser()

parsed = http_parser.parse_http_file("test.http")

parsed_curl = curl_parser.parse_curl_file("test.curl")

print(parsed)

print(parsed_curl)

for _ in [1,2]:
    print(_)