import geoip2.database
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CITY_DB = os.path.join(BASE_DIR, 'GeoLite2-City.mmdb')
ASN_DB = os.path.join(BASE_DIR, 'GeoLite2-ASN.mmdb')

reader_city = geoip2.database.Reader(CITY_DB)
reader_asn = geoip2.database.Reader(ASN_DB)

def enrich_ip(ip):
    result = {}

    try:
        city = reader_city.city(ip)
        result['country'] = city.country.name or ""
        result['city'] = city.city.name or ""
        result['region'] = city.subdivisions.most_specific.name or ""
        result['timezone'] = city.location.time_zone or ""
    except Exception:
        result.update({"country": "", "city": "", "region": "", "timezone": ""})

    try:
        asn = reader_asn.asn(ip)
        result['asn'] = str(asn.autonomous_system_number or "")
        result['org'] = asn.autonomous_system_organization or ""
    except Exception:
        result.update({"asn": "", "org": ""})

    return result
