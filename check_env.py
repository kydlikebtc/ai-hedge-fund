import os

keys = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'COINMARKETCAP_API_KEY': os.getenv('COINMARKETCAP_API_KEY')
}

for key, value in keys.items():
    if value and value != f'your_{key.lower()}_here':
        print(f'{key}: Available')
    else:
        print(f'{key}: Not available')
