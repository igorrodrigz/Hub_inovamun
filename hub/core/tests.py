from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from organizacoes.models import Organizacao
from territorio.models import Municipio


class OrganizationMapViewTests(TestCase):
	def setUp(self):
		self.staff = get_user_model().objects.create_user(
			username='map-staff',
			password='test-password',
			is_staff=True,
		)
		self.client.force_login(self.staff)

		self.georeferenced_municipio = Municipio.objects.create(
			nome='São Paulo',
			estado='São Paulo',
			uf='SP',
			latitude='-23.5505',
			longitude='-46.6333',
		)
		self.no_coordinates_municipio = Municipio.objects.create(
			nome='Campinas',
			estado='São Paulo',
			uf='SP',
		)
		self.inactive_municipio = Municipio.objects.create(
			nome='Município Inativo',
			estado='São Paulo',
			uf='SP',
			ativo=False,
			latitude='-22.9',
			longitude='-47.0',
		)

		Organizacao.objects.create(
			nome='Organização Mapeada',
			tipo=Organizacao.Tipo.STARTUP,
			cnpj='11223344556677',
			email='private-map-test@example.com',
			municipio=self.georeferenced_municipio,
		)
		Organizacao.objects.create(
			nome='Organização Inativa',
			tipo=Organizacao.Tipo.EMPRESA,
			cnpj='22334455667788',
			ativo=False,
			municipio=self.georeferenced_municipio,
		)
		Organizacao.objects.create(
			nome='Organização Sem Coordenadas',
			tipo=Organizacao.Tipo.EMPRESA,
			cnpj='33445566778899',
			municipio=self.no_coordinates_municipio,
		)
		Organizacao.objects.create(
			nome='Organização em Município Inativo',
			tipo=Organizacao.Tipo.INVESTIDOR,
			cnpj='44556677889900',
			municipio=self.inactive_municipio,
		)

	def test_map_shows_only_active_organizations_with_active_georeferenced_municipality(self):
		response = self.client.get(reverse('organization-map'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['map_organizations'], [{
			'name': 'Organização Mapeada',
			'type': Organizacao.Tipo.STARTUP,
			'city': 'São Paulo',
			'state': 'SP',
			'coordinates': [-46.6333, -23.5505],
		}])

	def test_map_response_does_not_include_private_organization_fields(self):
		response = self.client.get(reverse('organization-map'))

		self.assertNotContains(response, '11223344556677')
		self.assertNotContains(response, 'private-map-test@example.com')

	def test_anonymous_user_is_redirected_to_admin_login(self):
		self.client.logout()

		response = self.client.get(reverse('organization-map'))

		self.assertRedirects(
			response,
			'/admin/login/?next=/',
			fetch_redirect_response=False,
		)

	def test_authenticated_non_staff_user_cannot_access_map(self):
		user = get_user_model().objects.create_user(
			username='map-user',
			password='test-password',
		)
		self.client.force_login(user)

		response = self.client.get(reverse('organization-map'))

		self.assertRedirects(
			response,
			'/admin/login/?next=/',
			fetch_redirect_response=False,
		)
