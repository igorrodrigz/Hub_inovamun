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