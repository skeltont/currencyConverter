# currency converter

## setup
```
mkdir config
touch config/default.py
```
place this as the contents of `config/default.py`
```
CURRENCY_API_KEY = "<your freecurrencyapi.net key>"
```

## usage
```
docker compose up
```

## example endpoints
look up conversion rates
```
http://localhost:5000/conversion_rate?currency_from=usd&currency_to=gbp
```

convert a value between currency rates
```
http://localhost:5000/convert?convert_value=10&currency_from=usd&currency_to=gbp
```