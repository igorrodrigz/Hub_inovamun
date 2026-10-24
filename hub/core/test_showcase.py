from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from ecossistema.models import Categoria, Problema, Solucao, Conexao
from organizacoes.models import Organizacao
from territorio.models import Municipio


class ShowcaseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(username='editor', is_staff=True)
        cls.category = Categoria.objects.create(nome='Mobilidade')
        cls.city = Municipio.objects.create(nome='Uruguaiana', estado='Rio Grande do Sul', uf='RS')
        cls.organization = Organizacao.objects.create(nome='Rede Local', tipo='STARTUP', cnpj='12345678901234', email='privado@example.com', telefone='51999999999', municipio=cls.city)
        cls.problem = Problema.objects.create(titulo='Transporte municipal', categoria=cls.category, municipio=cls.city, descricao='<script>alert(1)</script>')
        cls.solution = Solucao.objects.create(titulo='Rotas inteligentes', organizacao=cls.organization, categoria=cls.category)

    def setUp(self):
        self.client.force_login(self.staff)

    def test_all_showcase_routes_require_staff(self):
        routes = [reverse('showcase-home')]
        for kind in ('problemas', 'solucoes', 'organizacoes'):
            routes.append(reverse('showcase-list', args=[kind]))
            routes.append(reverse('showcase-detail', args=[kind, self.problem.pk]))
        self.client.logout()
        for route in routes:
            with self.subTest(route=route):
                self.assertRedirects(self.client.get(route), '/admin/login/?next=' + route, fetch_redirect_response=False)
        user = get_user_model().objects.create_user(username='visitor')
        self.client.force_login(user)
        for route in routes:
            self.assertEqual(self.client.get(route).status_code, 302)

    def test_home_lists_open_problems(self):
        Problema.objects.create(titulo='Resolvido oculto dos destaques', status='RESOLVIDO')
        response = self.client.get(reverse('showcase-home'))
        self.assertContains(response, self.problem.titulo)
        self.assertNotContains(response, 'Resolvido oculto dos destaques')

    def test_filters_work_in_full_page_and_partial(self):
        Problema.objects.create(titulo='Saúde')
        route = reverse('showcase-list', args=['problemas'])
        params = {'q':'Transporte', 'categoria':str(self.category.pk), 'status':'ABERTO'}
        full = self.client.get(route, params)
        self.assertContains(full, 'Transporte municipal')
        self.assertNotContains(full, '>Saúde<')
        partial = self.client.get(route, params, HTTP_HX_REQUEST='true')
        self.assertContains(partial, 'Transporte municipal')
        self.assertNotContains(partial, '<html')
        self.assertIn('HX-Request', partial.headers['Vary'])
        restored = self.client.get(route, params, HTTP_HX_REQUEST='true', HTTP_HX_HISTORY_RESTORE_REQUEST='true')
        self.assertContains(restored, '<html')

    def test_inactive_dependencies_and_records_are_excluded(self):
        inactive_category = Categoria.objects.create(nome='Inativa', ativo=False)
        hidden = Problema.objects.create(titulo='Oculto', categoria=inactive_category)
        route = reverse('showcase-list', args=['problemas'])
        self.assertNotContains(self.client.get(route), 'Oculto')
        self.assertEqual(self.client.get(reverse('showcase-detail', args=['problemas', hidden.pk])).status_code,404)
        self.organization.ativo = False
        self.organization.save()
        self.assertNotContains(self.client.get(reverse('showcase-list', args=['solucoes'])), self.solution.titulo)
        self.assertEqual(self.client.get(reverse('showcase-detail', args=['solucoes', self.solution.pk])).status_code,404)
        self.city.ativo = False
        self.city.save()
        self.assertNotContains(self.client.get(route), self.problem.titulo)

    def test_details_escape_content_and_omit_contact_fields(self):
        for kind, item in [('problemas',self.problem),('solucoes',self.solution),('organizacoes',self.organization)]:
            response = self.client.get(reverse('showcase-detail', args=[kind,item.pk]))
            self.assertEqual(response.status_code,200)
            self.assertNotContains(response, self.organization.cnpj)
            self.assertNotContains(response, self.organization.email)
            self.assertNotContains(response, self.organization.telefone)
            self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertEqual(Conexao.objects.count(),0)

    def test_pagination_preserves_filters_and_handles_invalid_values(self):
        for i in range(11):
            Problema.objects.create(titulo=f'Transporte {i}')
        route = reverse('showcase-list', args=['problemas'])
        response = self.client.get(route, {'q':'Transporte','page':2})
        self.assertEqual(len(response.context['page_obj']),3)
        self.assertContains(response, 'q=Transporte')
        self.assertEqual(self.client.get(route, {'page':'abc'}).status_code,200)
        self.assertEqual(self.client.get(route, {'categoria':'9'*100}).context['page_obj'].paginator.count,0)
        self.assertEqual(self.client.get(route, {'categoria':'abc'}).status_code,200)

    def test_missing_relations_and_empty_catalog_render(self):
        item = Problema.objects.create(titulo='Sem contexto')
        self.assertContains(self.client.get(reverse('showcase-detail',args=['problemas',item.pk])), 'Sem categoria')
        self.assertContains(self.client.get(reverse('showcase-list',args=['problemas']), {'q':'inexistente'}), 'Nenhum resultado')
        self.assertEqual(self.client.get('/vitrine/inexistente/').status_code,404)
