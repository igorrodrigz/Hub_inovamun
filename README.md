# HUB

Plataforma para centralização e conexão de empresas, startups,
investidores, problemas e soluções dos municípios.

## Objetivo

Mapear o ecossistema territorial e facilitar conexões entre:

- Municípios
- Empresas
- Startups
- Investidores
- Problemas
- Soluções

## Stack

- Python
- Django
- PostgreSQL
- Django REST Framework (futuro)

## Mapa interno

O mapa de organizações fica na página inicial e requer um usuário autenticado com `is_staff=True`.
Ele usa os registros ativos e as coordenadas aproximadas do município; organizações sem município
georreferenciado não aparecem. Ao cadastrar ou revisar um município, informe seu código oficial IBGE
de sete dígitos. Se latitude e longitude estiverem ambas vazias, o Admin consulta a malha municipal
do IBGE pelo código e grava um ponto representativo dentro do território. Esse ponto não é
necessariamente o centro urbano. Coordenadas preenchidas manualmente são preservadas.

Se a consulta ao [serviço de Malhas do IBGE](https://servicodados.ibge.gov.br/api/docs/malhas)
falhar, o município continua salvo e o Admin mostra um aviso; salve novamente para tentar outra vez.
O serviço geométrico usa Shapely, instalado por `requirements.txt`.

Configure `API_MAPBOX` no arquivo `.env` com um token público do Mapbox. Esse token é enviado ao
navegador para renderizar o mapa; restrinja suas URLs permitidas na conta Mapbox. Sem o token, a
página apresenta uma mensagem de configuração em vez de falhar.

Para iniciar localmente a partir da raiz do projeto:

```powershell
pip install -r requirements.txt
cd hub
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` após autenticar-se. O login administrativo fica em
`http://127.0.0.1:8000/admin/`.
## Frontend — hub-01

A primeira entrega fica em `/vitrine/`, com início, catálogos e detalhes de problemas,
soluções e organizações. Todas essas rotas exigem staff nesta fase. O mapa segue em `/`.
Ainda não há regra de aprovação/publicação de cadastros; esta entrega não torna os dados públicos.
O catálogo omite CNPJ, e-mail e telefone. Ele não cria conexões nem altera status.

### Assets

Use Node.js 20 ou superior e execute na raiz:

```powershell
npm ci
npm run build
```

`npm run dev` recompila o CSS durante a edição. Tailwind é compilado localmente;
HTMX é copiado do pacote fixado para os estáticos, com sua licença. Os assets gerados
são versionados para que o Django funcione sem Node em runtime. Ao alterar templates
ou estilos, execute o build e versione o CSS atualizado.

### Desenvolvimento Django

Configure uma `SECRET_KEY` não vazia no `.env` da raiz e instale `requirements.txt`
em ambiente virtual. A partir de `hub/`:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Entre pelo `/admin/` e visite `/vitrine/`. Uma base vazia apresenta estados vazios;
os dados exibidos vêm dos cadastros reais. Não há fixtures de demonstração em produção.

Busca, categoria, status (problemas), tipo (organizações) e paginação usam GET e funcionam
sem JavaScript. HTMX atualiza resultados e URL. A restauração de histórico recebe uma
página completa; conteúdo interno não é armazenado no cache de histórico do HTMX.

### Política de visibilidade interna

- Todos os catálogos exigem registros ativos.
- Problemas e organizações com município inativo ficam ocultos; município ausente é aceito.
- Categoria inativa oculta problemas e soluções; categoria ausente é aceita.
- Soluções exigem organização ativa e município da organização ativo ou ausente.
- Detalhes seguem os mesmos critérios e retornam 404 para itens ocultos.

### Validação

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Os testes da vitrine cobrem permissões, filtros completos/parciais, histórico HTMX,
paginação, entradas inválidas, dependências inativas, relações ausentes, escape HTML
e ausência de contatos. Não houve alteração de modelos ou migrações nesta entrega.
