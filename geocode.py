import argparse
import logging
import os
import json
import urllib, urllib2

def build_url(api_key, country):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    url += 'key=' + api_key
    url += '&address=' + urllib.quote(country)

    return url

def get_country_geo(results, country):
    if len(results) > 1:
        country_count = 0
        for result in results:
            if 'country' in result['types']:
                country_count += 1

        # Perform some basic sanity checking.

        if country_count == 0:
            logging.warning('no country location from for: %s' % country)
            return
        elif country_count > 1:
            logging.warning('multiple country locations found for: %s' % country)
            return

    for result in results:
        # Skip results that do not have the country type
        if 'country' not in result['types']:
            continue

        data = {
            "name": country,
            "formattedName": result['formatted_address'],
            "location": result['geometry']['location']
        }

        return data

def geocode(api_key, country):
    url = build_url(api_key, country)

    response = urllib2.urlopen(url)
    data = json.load(response)

    return get_country_geo(data['results'], country)

def read_countries(countries_path):
    logging.info('reading country data')
    with open(countries_path, 'r') as f:
        return f.read().splitlines()

def run(api_key, countries_path, output_path):
    countries = read_countries(countries_path)
    results = []

    logging.info('geocoding countries')

    for country in countries:
        geo = geocode(api_key, country)
        if geo:
            results.append(geo)

    logging.info('writing json output to %s' % output_path)

    with open(output_path, 'w') as outfile:
        json.dump(results, outfile)

    print_results(results)

def print_results(results):
    for result in results:
        location = result['location']
        print '%s,%s,%s' % (result['name'], location['lat'], location['lng'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--countries', required=True)
    parser.add_argument('-o','--output', default='output.json')
    parser.add_argument('-k','--key', required=True)

    args = parser.parse_args()

    countries_path = args.countries
    output_path = args.output
    api_key = args.key

    if not os.path.exists(countries_path):
        parser.error('Countries path does not exist')

    run(api_key, countries_path, output_path)

if __name__ == "__main__":
    main()