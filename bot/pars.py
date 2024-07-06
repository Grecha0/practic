import requests
from bs4 import BeautifulSoup
from values import client_id, client_secret
from database import record_token, update_token, get_token, get_vacancy_info

def get_access_token(client_id, client_secret):
    auth_url = "https://hh.ru/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(auth_url, data=data, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data.get("access_token")
        return access_token
    else:
        print(f"Failed to get access token. Status code: {response.status_code}, Response: {response.text}")
        return None

def fetch_vacancies(vacancy_name, user_id_vac):
    access_token = get_token()
    if access_token == "1":
        access_token = get_access_token(client_id, client_secret)
        if access_token:
            update_token(access_token)
    access_token = get_token()
    
    vacancies_list = []
    page = 0
    per_page = 100  # Максимальное количество вакансий на одной странице

    while True:
        response = requests.get(
            "https://api.hh.ru/vacancies",
            params={
                "text": vacancy_name,
                "page": page,
                "per_page": per_page
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            print(f"Failed to fetch vacancies. Status code: {response.status_code}, Response: {response.text}")
            break
        
        vacancies_dict = response.json()
        items = vacancies_dict.get("items", [])
        if not items:
            break
        
        print(f"Page {page + 1}")
        for vacancy in items:
            if vacancy.get("archived"):
                continue

            vacancy_info = {
                "name": vacancy.get("name"),
                "salary_from": "Не указано",
                "salary_to": "Не указано",
                "currency": "Не указано",
                "city": "Не указано"
            }

            if vacancy.get("salary"):
                vacancy_info["salary_from"] = vacancy["salary"].get("from")
                vacancy_info["salary_to"] = vacancy["salary"].get("to")
                vacancy_info["currency"] = vacancy["salary"].get("currency")

            if vacancy.get("area"):
                vacancy_info["city"] = vacancy["area"].get("name")
                
            name = vacancy.get("name")
            salary = vacancy.get("salary")
            id = vacancy.get('id')
            address = vacancy.get('address', {})
            metro = address.get('metro', {}) if address else {}
            metro_station = metro.get('station_name', 'N/A') if metro else 'Не указано'
            id = f"https://hh.ru/vacancy/{id}"
            if salary:
                salary_from = salary.get('from', 'N/A')
                salary_to = salary.get('to', 'N/A')
                currency = salary.get('currency', '')
            else:
                salary_from = 'Не указано'
                salary_to = 'Не указано'
                currency = 'Не указано'
            city = vacancy["area"].get("name")

            print(name, salary_from, salary_to, currency, city, metro_station, id)
            get_vacancy_info(name, salary_from, salary_to, currency, city, metro_station, id, user_id_vac)
        
        vacancies_list.extend(items)
        page += 1
    print(f"Total vacancies fetched: {len(vacancies_list)}")
    return vacancies_list

# Вызов функции
#vacancies = fetch_vacancies("Программист")
#print(f"Total vacancies fetched: {len(vacancies)}")
