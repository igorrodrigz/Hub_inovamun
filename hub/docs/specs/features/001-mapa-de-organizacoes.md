# Mapa de organizações

## Status

IMPLEMENTED

## Objetivo

Exibir organizações ativas no mapa da aplicação, posicionadas pela referência geográfica de seu município.

## Contexto

A V1 é operada pela equipe no Django Admin. Organizações pertencem opcionalmente a municípios, mas o domínio ainda não possui coordenadas nem endereço para geolocalização. A visualização será interna e não criará uma API pública.

## Requisitos funcionais

- RF01: disponibilizar o mapa na página inicial da aplicação, somente para usuários autenticados com permissão de staff.
- RF02: exibir organizações ativas associadas a municípios ativos com coordenadas cadastradas.
- RF03: permitir filtrar por Empresa, Startup e Investidor e abrir detalhes básicos no marcador.
- RF04: permitir que a equipe cadastre coordenadas de referência no Admin de Município.
- RF05: exibir somente nome, tipo e município no mapa; não enviar CNPJ, e-mail ou telefone ao navegador.
- RF06: armazenar o código oficial IBGE de sete dígitos como identificador único do município e chave de associação para referências geográficas.
- RF07: ao salvar um município sem coordenadas no Admin, obter a malha municipal do IBGE pelo código e gravar um ponto representativo dentro do limite geográfico.

## Regras de negócio

- RN01: a coordenada pertence ao Município e representa uma localização aproximada, não o endereço exato de cada organização.
- RN02: latitude e longitude são opcionais, mas devem ser informadas em conjunto e permanecer nos intervalos geográficos válidos.
- RN03: organizações sem município ou sem coordenadas municipais não aparecem no mapa.
- RN04: organizações e municípios inativos não aparecem no mapa.
- RN05: os pares GeoJSON usam longitude antes de latitude.
- RN06: novos municípios informados pelo Admin devem possuir código IBGE válido; cadastros legados sem código podem permanecer sem código até revisão, sem perder seus dados.
- RN07: o código IBGE identifica o município, mas não deve ser confundido com latitude/longitude nem sobrescrever coordenadas existentes.
- RN08: o preenchimento automático ocorre somente quando latitude e longitude estiverem ambas vazias; coordenadas já informadas manualmente são preservadas.
- RN09: o ponto derivado representa a área municipal e não garante corresponder ao centro urbano nem ao endereço de uma organização.
- RN10: falhas ou respostas inválidas do serviço do IBGE não impedem salvar o município; o Admin informa a falha e permite nova tentativa ao salvar novamente.

## Modelo de dados

Adicionar código IBGE único de sete dígitos e latitude/longitude decimais opcionais ao Município, com validação de formato, intervalo e consistência do par. Nenhuma alteração no modelo Organização.

## Fluxo

Staff informa o código IBGE no Admin. Se as coordenadas estiverem vazias, o sistema consulta a malha municipal do IBGE e grava um ponto representativo; caso já existam coordenadas, mantém os valores. Staff acessa a página inicial e visualiza as organizações elegíveis. O navegador recebe apenas os campos necessários para o mapa e filtros.

## Validações

- Rejeitar latitude fora de -90 a 90 e longitude fora de -180 a 180.
- Rejeitar o preenchimento de apenas uma coordenada.
- Rejeitar códigos IBGE fora do formato de sete dígitos e duplicados.
- Confirmar que o código retornado na geometria do IBGE corresponde ao código solicitado.
- Tratar timeout, erro HTTP, JSON inválido, geometria vazia ou código divergente sem descartar o município.
- Se o token público do Mapbox não estiver configurado, apresentar uma mensagem clara sem falha JavaScript.
- Usuários sem staff não podem acessar o mapa.

## Critérios de aceite

- [x] CA01: coordenadas podem ser cadastradas e editadas pelo Admin de Município.
- [x] CA02: o mapa apresenta somente organizações elegíveis e marcadores com longitude/latitude corretas.
- [x] CA03: filtros atualizam marcadores e contador.
- [x] CA04: usuários sem staff são redirecionados para autenticação ou recebem acesso negado.
- [x] CA05: testes cobrem coordenadas, visibilidade e conteúdo serializado.
- [x] CA06: código IBGE é validado, único e associado aos municípios existentes reconhecidos.
- [x] CA07: coordenadas ausentes são preenchidas a partir do ponto representativo da malha oficial do código IBGE.
- [x] CA08: coordenadas preexistentes são preservadas e falha do IBGE não impede o salvamento.

## Testes

Testar validação de código IBGE, unicidade e migração de município existente; cálculo e validação do ponto representativo; preenchimento e preservação de coordenadas no Admin; falha do serviço externo; validação de pares e intervalos; acesso staff; visibilidade do mapa e ausência de campos sensíveis na resposta.

## Impactos

Model e Admin de território, migração Django, serviço de consulta à API de Malhas do IBGE, dependência Shapely, testes e documentação. O serviço é acionado no Admin apenas quando as coordenadas estão vazias; não altera organizações nem a exposição de dados do mapa.