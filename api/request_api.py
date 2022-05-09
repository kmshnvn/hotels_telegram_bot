# import requests
# import json
# import re
# from loguru import logger
# from fuzzywuzzy import process
# from config_data.config import headers, location_url, hotel_url, photo_url
#
#
# def request_to_api(url, querystring):
#     try:
#         response = requests.get(url, headers=headers, params=querystring, timeout=10)
#
#         if response.status_code == requests.codes.ok:
#             logger.info(response.status_code)
#             return
#         else:
#             raise Exception(f'Ошибка {response.status_code} при запросе к API')
#     except Exception as api_ex:
#         logger.error(api_ex)
#         raise TimeoutError('Время ожидания запроса превышено')
#
#
# def get_city(city: str):
#     try:
#         #Проверка города и его перевод на англ
#         querystring = {"query": city, "locale": "en_US", "currency": "USD"}
#
#         if request_to_api(location_url, querystring):
#             response = requests.request("GET", location_url, headers=headers, params=querystring, timeout=10)
#
#             pattern = r'(?<="CITY_GROUP",).+?[\]]'
#             find = re.search(pattern, response.text)
#
#             if find:
#                 suggestions = json.loads(f"{{{find[0]}}}")
#                 cities = list()
#                 with open('data.json', 'w') as file:
#                     json.dump(suggestions, file, indent=4)
#                 # for dest_id in suggestions['entities']:  # Обрабатываем результат
#                 #     # clear_destination = re.sub(  dest_id['caption'])
#                 #     # cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
#                 #     return cities
#                 # else:
#                 #     raise Exception('Ошибка в обработке списка городов')
#             else:
#                 raise Exception('Города не найдено')
#     except Exception as city_ex:
#         logger.error(city_ex)
#
#
# # class GetInformation():
# #     def get_infomation(self):
# #         try:
# #             response = requests.request(
# #                 "GET", self.used_url,
# #                 headers=self.used_headers,
# #                 params=self.querystring, timeout=10
# #             )
# #
# #             if response.status_code == requests.codes.ok:
# #                 if response is not None:
# #                     data = json.loads(response.text)
# #                     return data["suggestions"][0]["entities"][0]["destinationId"]
# #                 else:
# #                     raise Exception('Ничего не найдено при запросе к API')
# #             else:
# #                 raise Exception(f'Ошибка {response.status_code} при запросе к API')
# #         except Exception as api_ex:
# #             logger.error(api_ex)
# #             raise TimeoutError('Время ожидания запроса превышено')
# #
# # def get_city_id(city, setting):
#
