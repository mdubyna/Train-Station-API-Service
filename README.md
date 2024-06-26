# Train Station API Service

Django project for managing train station

## How to run

```
git clone https://github.com/mdubyna/Train-Station-API-Service.git
cd train_station_api_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
Create new Postgres DB & User
Copy .env.sample -> .env and add your data
python manage.py migrate
python manage.py runserver
```

## Run with docker

Docker should be installed

```
docker-compose build
docker-compose up
```

## How to get access:

- create user via: `/api/user/register/`
- get access token via: `/api/user/token/`

## Features

- JWT authentication
- Admin panel: `/admin/`
- Documentation: `/api/doc/swagger/`
- Mapping orders and tickets
- Creating trips with routes and trains
- Add crew, train types and stations
