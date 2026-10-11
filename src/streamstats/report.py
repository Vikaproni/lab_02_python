'''Запись финального отчета в json-файл'''
import json


def writing_report(datas:dict,output_file:str = 'REPORT.json') -> None:
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(datas, file, ensure_ascii=False, indent=1)