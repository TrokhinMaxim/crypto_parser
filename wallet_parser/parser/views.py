import os
import re
import requests
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Transactions
from django.conf import settings
from .telegram_parser import parse_telegram_html, extract_latin_and_digits
from django.http import FileResponse
from django.shortcuts import HttpResponse

API_KEY = "d6b988fcb59d48e6839b618e556ea13a"

CURRENCY_URLS = {
    "BTC": "https://api.blockcypher.com/v1/btc/main",
    "ETH": "https://api.blockcypher.com/v1/eth/main",
    "DASH": "https://api.blockcypher.com/v1/dash/main",
}

def wallet_exists(wallet_address):
    return Transactions.objects.filter(wallet=wallet_address).exists()

def get_crypto_name(wallet_address):
    if re.match(r'^bc1', wallet_address):
        return "BTC"
    elif re.match(r'^0x', wallet_address, re.IGNORECASE):
        return "ETH"
    elif re.match(r'^X', wallet_address):
        return "DASH"
    # Добавьте другие условия для других криптовалют
    return None

def get_wallet_info(currency, wallet_address):
    if currency not in CURRENCY_URLS:
        return

    BASE_URL = CURRENCY_URLS[currency]
    API_TOKEN = API_KEY

    def get_wallet_balance(wallet_address):
        url = f"{BASE_URL}/addrs/{wallet_address}/balance"
        headers = {}
        if API_TOKEN:
            headers["token"] = API_TOKEN
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            balance_data = response.json()
            return balance_data.get("balance") / 10 ** 8
        else:
            print(f"Ошибка при получении баланса для кошелька {wallet_address}: {response.content}")
            return None

    def get_wallet_transactions(wallet_address):
        url = f"{BASE_URL}/addrs/{wallet_address}/full"
        headers = {}
        if API_TOKEN:
            headers["token"] = API_TOKEN
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("txs", [])
        else:
            print(f"Ошибка при получении истории транзакций для кошелька {wallet_address}: {response.content}")
            return None

    balance = get_wallet_balance(wallet_address)
    if balance is None:
        return

    formatted_balance = int(balance)

    transactions = get_wallet_transactions(wallet_address)
    if transactions:
        crypto_name = get_crypto_name(wallet_address)  # Получаем название крипты
        if crypto_name:
            # Сохранение данных транзакции в модель с указанием названия криптовалюты
            if not wallet_exists(wallet_address):
                transaction = Transactions(
                    receiver=wallet_address,
                    sender=', '.join(set(input_.get("addresses")[0] for tx in transactions for input_ in tx.get("inputs", []) if tx.get("addresses"))),
                    balance=formatted_balance,
                    wallet=wallet_address,
                    crypto_name=crypto_name  # Добавляем название крипты
                )
                transaction.save()
    else:
        print(f"История транзакций не найдена или произошла ошибка для кошелька {wallet_address}")

from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            app_directory = os.path.dirname(os.path.abspath(__file__))
            upload_file_path = os.path.join(app_directory, 'data', uploaded_file.name)

            with open(upload_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            parse_telegram_html(uploaded_file.name)  # Передаем только имя файла

            file_path = os.path.join(app_directory, 'data', 'filtered_messages.txt')
            latin_and_digits = extract_latin_and_digits(file_path)

            unique_latin_and_digits = list(set(latin_and_digits))

            for item in unique_latin_and_digits:
                if len(item) > 25:
                    crypto_name = get_crypto_name(item)
                    if crypto_name:
                        get_wallet_info(crypto_name, item)
                        print(item)

            return HttpResponseRedirect(reverse('download_database'))

    else:
        form = UploadFileForm()

    return render(request, 'main.html', {'form': form})

def download_database(request):
    database_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')  # Путь к вашей базе данных
    if os.path.exists(database_path):
        return FileResponse(open(database_path, 'rb'), as_attachment=True, filename='db.sqlite3')
    else:
        return HttpResponse("База данных не найдена", status=404)