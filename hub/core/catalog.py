from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.vary import vary_on_headers

from ecossistema.models import Categoria, Problema, Solucao
from organizacoes.models import Organizacao

CATALOGS = {
    'problemas': ('Problemas', 'Conheça os desafios dos municípios e encontre oportunidades para colaborar.'),
    'solucoes': ('Soluções', 'Explore conhecimento e soluções oferecidas pelas organizações do ecossistema.'),
    'organizacoes': ('Organizações', 'Conheça empresas, startups e investidores que fazem parte desta rede.'),
}


def catalog_queryset(kind):
    if kind == 'problemas':
        return Problema.objects.filter(ativo=True).filter(Q(municipio__isnull=True) | Q(municipio__ativo=True)).filter(Q(categoria__isnull=True) | Q(categoria__ativo=True)).select_related('municipio', 'categoria').order_by('titulo', 'pk')
    if kind == 'solucoes':
        return Solucao.objects.filter(ativo=True, organizacao__ativo=True).filter(Q(organizacao__municipio__isnull=True) | Q(organizacao__municipio__ativo=True)).filter(Q(categoria__isnull=True) | Q(categoria__ativo=True)).select_related('organizacao', 'categoria').order_by('titulo', 'pk')
    if kind == 'organizacoes':
        return Organizacao.objects.filter(ativo=True).filter(Q(municipio__isnull=True) | Q(municipio__ativo=True)).select_related('municipio').order_by('nome', 'pk')
    raise Http404('Catálogo não encontrado.')


@staff_member_required(login_url='admin:login')
def home(request):
    return render(request, 'core/home.html', {
        'problem_count': catalog_queryset('problemas').count(),
        'solution_count': catalog_queryset('solucoes').count(),
        'organization_count': catalog_queryset('organizacoes').count(),
        'problems': catalog_queryset('problemas').filter(status=Problema.Status.ABERTO)[:3],
    })


@staff_member_required(login_url='admin:login')
@vary_on_headers('HX-Request', 'HX-History-Restore-Request')
def catalog(request, kind):
    queryset = catalog_queryset(kind)
    filters = {key: request.GET.get(key, '').strip()[:100] for key in ('q', 'categoria', 'status', 'tipo')}
    if filters['q']:
        field = 'nome' if kind == 'organizacoes' else 'titulo'
        queryset = queryset.filter(Q(**{field + '__icontains': filters['q']}) | Q(descricao__icontains=filters['q']))
    if kind != 'organizacoes' and filters['categoria']:
        category = filters['categoria']
        queryset = queryset.filter(categoria_id=int(category)) if category.isascii() and category.isdigit() and len(category) < 10 else queryset.none()
    if kind == 'problemas' and filters['status']:
        queryset = queryset.filter(status=filters['status'])
    if kind == 'organizacoes' and filters['tipo']:
        queryset = queryset.filter(tipo=filters['tipo'])
    params = request.GET.copy()
    params.pop('page', None)
    query = params.urlencode()
    context = {
        'kind': kind, 'heading': CATALOGS[kind][0], 'introduction': CATALOGS[kind][1],
        'page_obj': Paginator(queryset, 9).get_page(request.GET.get('page')),
        'filters': filters, 'categories': Categoria.objects.filter(ativo=True),
        'statuses': Problema.Status.choices, 'types': Organizacao.Tipo.choices,
        'page_query': query + '&' if query else '',
    }
    partial = request.headers.get('HX-Request') == 'true' and request.headers.get('HX-History-Restore-Request') != 'true'
    return render(request, 'core/components/results.html' if partial else 'core/catalog.html', context)


@staff_member_required(login_url='admin:login')
def detail(request, kind, pk):
    item = get_object_or_404(catalog_queryset(kind), pk=pk)
    context = {'kind': kind, 'heading': CATALOGS[kind][0], 'item': item,
               'title': item.nome if kind == 'organizacoes' else item.titulo}
    if kind == 'organizacoes':
        context['solutions'] = catalog_queryset('solucoes').filter(organizacao=item)
    return render(request, 'core/detail.html', context)
