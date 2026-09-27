import gzip
import json
from decimal import Decimal
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from shapely.geometry import shape


class IBGECoordinateError(Exception):
    pass


def get_municipality_reference_coordinates(codigo_ibge):
    if len(codigo_ibge) != 7 or not codigo_ibge.isdigit():
        raise IBGECoordinateError('O código IBGE deve conter sete dígitos.')

    query = urlencode({
        'formato': 'application/vnd.geo+json',
        'qualidade': 'minima',
    })
    url = f'https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{codigo_ibge}?{query}'
    request = Request(url, headers={'User-Agent': 'HUB-MunicipalMap/1.0'})

    try:
        with urlopen(request, timeout=8) as response:
            content = response.read()
            if content.startswith(b'\x1f\x8b'):
                content = gzip.decompress(content)
            payload = json.loads(content)
    except (URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise IBGECoordinateError('Não foi possível consultar a malha do IBGE.') from error

    if not isinstance(payload, dict) or not isinstance(payload.get('features'), list):
        raise IBGECoordinateError('A resposta do IBGE não contém uma FeatureCollection válida.')

    matches = []
    for feature in payload['features']:
        if not isinstance(feature, dict):
            continue
        properties = feature.get('properties')
        if isinstance(properties, dict) and str(properties.get('codarea', '')) == codigo_ibge:
            matches.append(feature)

    if len(matches) != 1:
        raise IBGECoordinateError('A malha retornada não corresponde ao código IBGE informado.')

    try:
        geometry_data = matches[0].get('geometry')
        if not isinstance(geometry_data, dict):
            raise ValueError('A geometria está ausente.')
        geometry = shape(geometry_data)
        if geometry.geom_type not in ('Polygon', 'MultiPolygon'):
            raise ValueError('A geometria não é poligonal.')
        point = geometry.representative_point()
    except (KeyError, TypeError, ValueError) as error:
        raise IBGECoordinateError('A geometria retornada pelo IBGE é inválida.') from error

    if geometry.is_empty or point.is_empty or not geometry.covers(point):
        raise IBGECoordinateError('A geometria retornada pelo IBGE não contém um ponto válido.')

    return (
        Decimal(str(point.y)).quantize(Decimal('0.000001')),
        Decimal(str(point.x)).quantize(Decimal('0.000001')),
    )