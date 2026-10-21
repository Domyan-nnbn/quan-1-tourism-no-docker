"""Create a checked, editable POI draft from a single Wikipedia URL."""
import re
import unicodedata
from math import radians, sin, cos, atan2, sqrt
from urllib.parse import unquote, urlsplit

import httpx
from fastapi import HTTPException
from sqlalchemy import select

from ..models import Content, POI
from ..repositories import common as persistence
from .common import audit, serialize
from ..worker import fetch_wikipedia


def _normalize(value: str) -> str:
    value = unicodedata.normalize('NFKD', value.casefold())
    value = ''.join(c for c in value if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def _distance_m(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(p1)*cos(p2)*sin(dlon/2)**2
    return 6371000 * 2 * atan2(sqrt(a), sqrt(1-a))


def _wiki_metadata(url):
    parts = urlsplit(url)
    lang = 'vi' if parts.netloc == 'vi.wikipedia.org' else 'en'
    title = unquote(parts.path[6:]).replace('_', ' ')
    endpoint = f'https://{parts.netloc}/w/api.php'
    headers = {'User-Agent': 'Quan1TourismStudent/1.0 (educational prototype)'}
    try:
        with httpx.Client(timeout=15, follow_redirects=False, headers=headers) as client:
            response = client.get(endpoint, params={
                'action': 'query', 'format': 'json', 'formatversion': 2,
                'redirects': 1, 'prop': 'pageprops|coordinates', 'ppprop': 'wikibase_item',
                'titles': title,
            })
            response.raise_for_status()
            page = response.json()['query']['pages'][0]
            if page.get('missing') or not page.get('coordinates'):
                raise HTTPException(422, 'Bài Wikipedia không có tọa độ để xác minh địa điểm.')
            item_id = page.get('pageprops', {}).get('wikibase_item')
            if not item_id:
                raise HTTPException(422, 'Không tìm thấy mã Wikidata để kiểm tra địa điểm trùng.')
            coordinate = page['coordinates'][0]
            labels_response = client.get('https://www.wikidata.org/w/api.php', params={
                'action': 'wbgetentities', 'format': 'json', 'ids': item_id,
                'props': 'labels', 'languages': 'vi|en',
            })
            labels_response.raise_for_status()
            labels = labels_response.json().get('entities', {}).get(item_id, {}).get('labels', {})
            source_title = page['title']
            name_vi = labels.get('vi', {}).get('value') or (source_title if lang == 'vi' else '')
            name_en = labels.get('en', {}).get('value') or (source_title if lang == 'en' else '')
            return lang, source_title, name_vi, name_en, item_id, float(coordinate['lat']), float(coordinate['lon'])
    except HTTPException:
        raise
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(502, 'Không đọc được metadata Wikipedia. Kiểm tra URL hoặc thử lại.') from exc


def _district_address(lat, lon):
    try:
        response = httpx.get('https://nominatim.openstreetmap.org/reverse', params={
            'format': 'jsonv2', 'lat': lat, 'lon': lon, 'zoom': 18,
            'addressdetails': 1, 'accept-language': 'vi,en',
        }, headers={'User-Agent': 'Quan1TourismStudent/1.0 (educational prototype; contact: admin@quan1.local)'}, timeout=15)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, 'Không xác minh được địa chỉ qua OpenStreetMap. Thử lại sau.') from exc
    address = result.get('address') or {}
    district_values = [str(address.get(k, '')).strip().casefold() for k in
                       ('city_district', 'district', 'suburb', 'county', 'state_district')]
    district1 = any(re.search(r'(^|\b)(quận\s*1|quan\s*1|district\s*1|q\.?\s*1)(\b|$)', value)
                    for value in district_values)
    hcm_values = [str(address.get(k, '')).casefold() for k in
                  ('city', 'municipality', 'state', 'province', 'city_district')]
    in_hcmc = any('ho chi minh' in value or 'hồ chí minh' in value or 'saigon' in value
                  for value in hcm_values)
    full_address = result.get('display_name', '')
    if not district1 and not full_address:
        raise HTTPException(422, 'Không xác định được địa chỉ hành chính của tọa độ Wikipedia.')
    return district1 and in_hcmc, full_address


def import_from_wikipedia(source_url, admin, db):
    lang, title, name_vi, name_en, item_id, lat, lon = _wiki_metadata(source_url)
    in_district, address = _district_address(lat, lon)
    if not in_district:
        raise HTTPException(422, f'Tọa độ bài Wikipedia được định vị tại “{address}”, chưa xác minh thuộc Quận 1.')

    existing = db.scalars(select(POI)).all()
    candidate_names = {_normalize(name_vi), _normalize(name_en), _normalize(title)} - {''}
    duplicate = None
    for poi in existing:
        versions = db.scalars(select(Content).where(Content.poi_id == poi.id)).all()
        sources = [v.source or {} for v in versions]
        if any(s.get('wikidata_id') == item_id for s in sources):
            duplicate = (poi, 'cùng mã Wikidata')
            break
        names = {_normalize(poi.name), _normalize(poi.name_en)}
        if candidate_names & names:
            duplicate = (poi, 'trùng tên')
            break
        if _distance_m(lat, lon, poi.latitude, poi.longitude) <= 75:
            duplicate = (poi, 'tọa độ cách dưới 75 m')
            break
    if duplicate:
        poi, reason = duplicate
        raise HTTPException(409, f'Địa điểm có thể đã tồn tại ({reason}): {poi.name} · {poi.id}')

    try:
        plain, source = fetch_wikipedia(source_url)
    except Exception as exc:
        raise HTTPException(502, f'Không trích xuất được nội dung bài Wikipedia: {type(exc).__name__}.') from exc

    poi = POI(name=(name_vi or title)[:150], name_en=(name_en or title)[:150], category='landmark', address=address[:250],
              latitude=lat, longitude=lon, radius=30, source_url=source_url,
              geofence_type='circle', exit_buffer_m=20, dwell_seconds=10,
              gps_accuracy_threshold_m=25)
    persistence.add(db, poi)
    db.flush()
    source.update({'wikidata_id': item_id, 'location_source': 'OpenStreetMap reverse geocoding',
                   'location_verified': True, 'district_check': 'District 1'})
    content = Content(poi_id=poi.id, vi=plain if lang == 'vi' else '',
                      en=plain if lang == 'en' else '', zh='', fr='', ja='',
                      state='DRAFT', source=source)
    persistence.add(db, content)
    db.flush()
    audit(db, admin, 'import_wikipedia_url', poi.id)
    db.commit()
    return serialize(db, poi, True)
