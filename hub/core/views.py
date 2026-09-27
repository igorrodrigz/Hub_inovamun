from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from organizacoes.models import Organizacao


@staff_member_required(login_url='admin:login')
def organization_map(request):
	organizations = Organizacao.objects.filter(
		ativo=True,
		municipio__ativo=True,
		municipio__latitude__isnull=False,
		municipio__longitude__isnull=False,
	).values(
		'nome',
		'tipo',
		'municipio__nome',
		'municipio__uf',
		'municipio__latitude',
		'municipio__longitude',
	)

	map_organizations = [
		{
			'name': organization['nome'],
			'type': organization['tipo'],
			'city': organization['municipio__nome'],
			'state': organization['municipio__uf'],
			'coordinates': [
				float(organization['municipio__longitude']),
				float(organization['municipio__latitude']),
			],
		}
		for organization in organizations
	]

	return render(request, 'index.html', {
		'map_organizations': map_organizations,
		'mapbox_access_token': settings.MAPBOX_ACCESS_TOKEN,
	})
