import requests
import json

# VDV-777. Настройки (Репо нэйм итд тоже просто меняешь на свое, в качестве примера для сверки посмотрев репу https://github.com/vdv-777/TF.
# verify=False сделан как временное решение, можно убрать, если все потом наладишь с ключами, это будет более по феншую)
# Получившийся JSON - можно скармливать любой нейросети, чтобы передать в ее контекст всю иерархию объектов из репозитория и их код
# На основе поданного на вход нейросети сжатого контекста из иерархии и кода объектов - можно приступать к доработке по своим требованиям
# Либо для подготовки любых readme, описаний кода, использованных переменных итд и их автоматической актуализации
TOKEN = 'Скопируй в эту переменную твой гитхаб-токен'
REPO_OWNER = 'vdv-777'
REPO_NAME = 'TF'
BRANCH_OR_COMMIT_SHA = 'main'
OUTPUT_FILE = 'full_repo_metadata.json'

headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3.raw'}

def fetch_tree():
    """Получаем структуру файлов"""
    response = requests.get(
        f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH_OR_COMMIT_SHA}?recursive=true',
        headers={'Authorization': f'token {TOKEN}'},
        verify=False  #
    )
    if response.status_code != 200:
        raise Exception(f"Ошибка при получении дерева файлов: {response.status_code}, {response.text}")
    return response.json()['tree']

def download_blob(blob_sha):
    """Загружаем содержимое файла"""
    response = requests.get(
        f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_OR_COMMIT_SHA}/{blob_sha}',
        headers=headers,
        verify=False  #
    )
    if response.status_code != 200:
        raise Exception(f"Ошибка при загрузке файла: {response.status_code}, {response.text}")
    # Декодируем текст в UTF-8 явно
    return response.content.decode('utf-8')

def process_files(file_list):
    full_data = []
    for item in file_list:
        if item['type'] == 'blob':
            try:
                content = download_blob(item['path'])
                entry = {
                    'path': item['path'],
                    'content': content
                }
                full_data.append(entry)
            except Exception as e:
                print(f"Пропуск файла {item['path']} из-за ошибки: {e}")
    return full_data

def save_to_json(data):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

try:
    file_tree = fetch_tree()
    processed_data = process_files(file_tree)
    save_to_json(processed_data)
    print(f"Данные успешно сохранены в {OUTPUT_FILE}.")
except Exception as e:
    print(f"Возникла ошибка: {e}")