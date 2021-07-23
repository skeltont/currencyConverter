from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

app.config.from_pyfile('config/default.py')

# support US Dollars, British Pounds Sterling, and Euros.
# USD, GBP, EUR


class ConversionCurrencyException(Exception):
    '''simple exception class for when the currency provided
    is invalid or unsupported'''


class ConversionLookupException(Exception):
    '''simple exception class for when the currency provided
    is not found within the payload.'''


def get_conversion_rate(currency_from, currency_to):
    url = (
        "https://freecurrencyapi.net/api/v1/rates"
        f"?base_currency={currency_from}"
        f"&apikey={app.config['CURRENCY_API_KEY']}"
    )
    response = requests.request("GET", url)

    payload = response.json()
    most_recent = list(payload["data"].keys())[-1]
    try:
        rate = payload["data"][most_recent][currency_to]
    except KeyError as err:
        app.logger.critical(
            f"payload did not contain required currency: f{payload}"
        )
        
        raise ConversionLookupException(
            'payload did not contain conversion rates.') from err

    return rate


def validate_and_format_currency(currency):
    '''make sure it's one of the required types so we don't take any
    bad values'''

    if not isinstance(currency, str):
        raise ConversionCurrencyException(
            f'invalid currency type provieded: {type(currency)}')

    if currency.upper() not in ['USD', 'GBP', 'EUR']:
        raise ConversionCurrencyException(
            f'invalid currency provided: {currency}')

    return currency.upper()


@app.route('/conversion_rate')
def conversion_rate():
    '''a GET endpoint to get a currency rate
    Returns the conversion rate from currency1 to currency2 as a floating point number.
    The rate should be the value of 1 unit of currency1 in currency2.
    The return value should be a JSON object restating the request parameters and the rate.
    ''' 

    currency_from = request.args.get('currency_from', '')
    currency_to = request.args.get('currency_to', '')

    try:
        currency_from = validate_and_format_currency(currency_from)
        currency_to = validate_and_format_currency(currency_to)
    except ConversionCurrencyException as err:
        return jsonify({'response': f"Failed: {err}"}), 403

    try:
        rate = get_conversion_rate(currency_from, currency_to)
    except ConversionLookupException:
        return jsonify({'response': "Failed to find conversion rate"}), 404

    return jsonify({
        'response': {
            'currency_from': currency_from,
            'currency_to': currency_to,
            'conversion_rate': rate
        }
    })


@app.route('/convert/')
def convert():
    '''a GET endpoint that converts a value in one currency to another
    returns an amount in one currency, converted to an amount in another currency.
    The return value should be a JSON object restating the request parameters and the converted amount.
    All results should be rounded to 2 decimal points.
    '''

    convert_value = request.args.get('convert_value')
    currency_from = request.args.get('currency_from', '')
    currency_to = request.args.get('currency_to', '')

    try:
        currency_from = validate_and_format_currency(currency_from)
        currency_to = validate_and_format_currency(currency_to)

        convert_value = float(convert_value)
    except ConversionCurrencyException as err:
        return jsonify({'response': f"Failed: {err}"}), 403
    except ValueError:
        return jsonify({'response': 'invalid convert_value supplied'}), 403

    try:
        rate = get_conversion_rate(currency_from, currency_to)
    except ConversionLookupException:
        return jsonify({'response': "Failed to find conversion rate"}), 404

    converted_value = convert_value * float(rate)

    return jsonify({
        'response': {
            'currency_from': currency_from,
            'currency_to': currency_to,
            'conversion_rate': rate,
            'convert_value': convert_value,
            'converted_value': converted_value
        }
    })
