import gzip
import json
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.test import RequestFactory, SimpleTestCase, TestCase
from urllib.error import URLError

from .admin import MunicipioAdmin
from .models import Municipio
from .services import IBGECoordinateError, get_municipality_reference_coordinates


class MunicipioCoordinateTests(TestCase):
	def build_municipio(self, **coordinates):
		return Municipio(
			nome='Campinas',
			estado='São Paulo',
			uf='SP',
			codigo_ibge='3509502',
			**coordinates,
		)

	def test_coordinates_must_be_provided_together(self):
		municipio = self.build_municipio(latitude=Decimal('-22.9056'))

		with self.assertRaises(ValidationError):
			municipio.full_clean()

	def test_coordinates_accept_geographic_boundaries(self):
		municipio = self.build_municipio(
			latitude=Decimal('90'),
			longitude=Decimal('180'),
		)

		municipio.full_clean()

	def test_coordinates_outside_geographic_bounds_are_rejected(self):
		municipio = self.build_municipio(
			latitude=Decimal('90.000001'),
			longitude=Decimal('180'),
		)

		with self.assertRaises(ValidationError):
			municipio.full_clean()


class MunicipioIbgeCodeTests(TestCase):
	def build_municipio(self, codigo_ibge):
		return Municipio(
			nome='Uruguaiana',
			estado='Rio Grande do Sul',
			uf='RS',
			codigo_ibge=codigo_ibge,
		)

	def test_code_must_have_seven_digits(self):
		municipio = self.build_municipio('432240')

		with self.assertRaises(ValidationError):
			municipio.full_clean()

	def test_code_must_be_unique(self):
		self.build_municipio('4322400').save()
		duplicate = self.build_municipio('4322400')

		with self.assertRaises(ValidationError):
			duplicate.full_clean()

	def test_admin_requires_ibge_code(self):
		municipio_admin = MunicipioAdmin(Municipio, AdminSite())
		form = municipio_admin.get_form(RequestFactory().get('/admin/'))

		self.assertTrue(form.base_fields['codigo_ibge'].required)


class IBGEMunicipalityCoordinatesTests(SimpleTestCase):
	def setUp(self):
		self.payload = {
			'type': 'FeatureCollection',
			'features': [{
				'type': 'Feature',
				'properties': {'codarea': '4322400'},
				'geometry': {
					'type': 'Polygon',
					'coordinates': [[
						[-47, -23], [-46, -23], [-46, -22], [-47, -22], [-47, -23],
					]],
				},
			}],
		}

	def mocked_response(self, content):
		response = MagicMock()
		response.__enter__.return_value = response
		response.read.return_value = content
		return response

	def test_returns_latitude_then_longitude_from_matching_ibge_geometry(self):
		content = json.dumps(self.payload).encode()
		with patch('territorio.services.urlopen', return_value=self.mocked_response(content)):
			coordinates = get_municipality_reference_coordinates('4322400')

		self.assertEqual(coordinates, (Decimal('-22.500000'), Decimal('-46.500000')))

	def test_reads_gzip_response_from_ibge(self):
		content = gzip.compress(json.dumps(self.payload).encode())
		with patch('territorio.services.urlopen', return_value=self.mocked_response(content)):
			coordinates = get_municipality_reference_coordinates('4322400')

		self.assertEqual(coordinates, (Decimal('-22.500000'), Decimal('-46.500000')))

	def test_rejects_invalid_feature_collection(self):
		content = json.dumps({'features': None}).encode()
		with patch('territorio.services.urlopen', return_value=self.mocked_response(content)):
			with self.assertRaises(IBGECoordinateError):
				get_municipality_reference_coordinates('4322400')

	def test_rejects_geometry_for_a_different_ibge_code(self):
		content = json.dumps(self.payload).encode()
		with patch('territorio.services.urlopen', return_value=self.mocked_response(content)):
			with self.assertRaises(IBGECoordinateError):
				get_municipality_reference_coordinates('3509502')

	def test_converts_network_failure_to_domain_error(self):
		with patch('territorio.services.urlopen', side_effect=URLError('offline')):
			with self.assertRaises(IBGECoordinateError):
				get_municipality_reference_coordinates('4322400')


class MunicipioAdminCoordinateAutofillTests(TestCase):
	def setUp(self):
		self.admin = MunicipioAdmin(Municipio, AdminSite())
		self.admin.message_user = Mock()
		self.request = RequestFactory().post('/admin/territorio/municipio/add/')

	def make_municipio(self, **coordinates):
		return Municipio(
			nome='Uruguaiana',
			estado='Rio Grande do Sul',
			uf='RS',
			codigo_ibge='4322400',
			**coordinates,
		)

	@patch('territorio.admin.get_municipality_reference_coordinates')
	def test_autofills_coordinates_when_missing(self, get_coordinates):
		get_coordinates.return_value = (Decimal('-29.795300'), Decimal('-56.812094'))
		municipio = self.make_municipio()

		self.admin.save_model(self.request, municipio, form=None, change=False)

		municipio.refresh_from_db()
		self.assertEqual(municipio.latitude, Decimal('-29.795300'))
		self.assertEqual(municipio.longitude, Decimal('-56.812094'))
		get_coordinates.assert_called_once_with('4322400')

	@patch('territorio.admin.get_municipality_reference_coordinates')
	def test_preserves_coordinates_already_entered(self, get_coordinates):
		municipio = self.make_municipio(
			latitude=Decimal('-23.550500'),
			longitude=Decimal('-46.633360'),
		)

		self.admin.save_model(self.request, municipio, form=None, change=False)

		municipio.refresh_from_db()
		self.assertEqual(municipio.latitude, Decimal('-23.550500'))
		self.assertEqual(municipio.longitude, Decimal('-46.633360'))
		get_coordinates.assert_not_called()

	@patch('territorio.admin.get_municipality_reference_coordinates', side_effect=IBGECoordinateError)
	def test_saves_municipality_when_ibge_lookup_fails(self, get_coordinates):
		municipio = self.make_municipio()

		self.admin.save_model(self.request, municipio, form=None, change=False)

		self.assertTrue(Municipio.objects.filter(codigo_ibge='4322400').exists())
		self.assertEqual(self.admin.message_user.call_args.kwargs['level'], messages.WARNING)
		get_coordinates.assert_called_once_with('4322400')

