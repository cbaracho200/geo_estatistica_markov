# Sistema de Geoestatística Imobiliária - Flask com Frontend Integrado

Sistema completo de análise espacial de dados imobiliários com **Flask + Jinja2 + Leaflet**, design minimalista preto e branco.

## 🎨 Frontend Integrado

Este projeto Flask inclui um frontend completo integrado diretamente no servidor Flask usando:
- **Templates Jinja2** para renderização server-side
- **JavaScript Vanilla** para interatividade
- **Leaflet** para visualização de mapas
- **CSS minimalista** preto e branco com tipografia monospace

### 🏗️ Estrutura

```
backend_flask/
│
├── app.py                  # Aplicação Flask principal
├── spatial_engine.py       # Motor de análise espacial
├── requirements.txt        # Dependências Python
│
├── templates/              # Templates Jinja2
│   ├── base.html          # Template base
│   ├── index.html         # Página principal (mapa)
│   ├── stats.html         # Página de estatísticas
│   └── api_docs.html      # Documentação da API
│
└── static/                # Arquivos estáticos
    ├── css/
    │   └── style.css      # Estilos minimalistas
    └── js/
        └── app.js         # Lógica do frontend
```

## 🚀 Início Rápido

### 1. Instalação

```bash
cd backend_flask
pip install -r requirements.txt
```

### 2. Executar o servidor

**Desenvolvimento (com auto-reload):**
```bash
python app.py
# ou
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000 --reload
```

**Produção (com Gunicorn):**
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
```

### 3. Acessar a aplicação

Abra o navegador em:
- **Frontend:** http://localhost:8000
- **Estatísticas:** http://localhost:8000/stats-page
- **Documentação API:** http://localhost:8000/api-docs
- **API Health:** http://localhost:8000/health

## 📄 Páginas Disponíveis

### 1. Página Principal (/)

Interface completa com:
- **Painel de controle lateral** com:
  - Upload de arquivos Parquet (lotes e imóveis)
  - Estatísticas em tempo real
  - Filtros de visualização (bairro, limite)
  - Controles de camadas (mostrar/ocultar)
  - Análise espacial configurável
- **Mapa interativo** com:
  - Visualização de lotes (polígonos pretos)
  - Visualização de imóveis (marcadores cinza)
  - Popups informativos ao clicar
  - Análise por raio (clique no mapa)

### 2. Estatísticas (/stats-page)

Página dedicada com:
- Total de lotes e imóveis
- Contagem com geometria
- Bairros únicos
- Atualização em tempo real

### 3. Documentação da API (/api-docs)

Documentação completa de todos os endpoints:
- Métodos HTTP
- Parâmetros
- Exemplos de requisições (curl)
- Exemplos de respostas

## 🎨 Design Minimalista

### Paleta de Cores
- **Preto:** `#000000` (texto, bordas, elementos principais)
- **Branco:** `#ffffff` (fundo)
- **Cinza claro:** `#f5f5f5` (painéis)
- **Cinza médio:** `#cccccc` (bordas secundárias)
- **Cinza escuro:** `#666666` (elementos de mapa)

### Tipografia
- **Fonte:** Courier New (monospace)
- **Tamanhos:** 12px, 14px, 16px, 18px
- **Espaçamento de letras:** 1-2px para títulos

### Elementos
- **Bordas:** 2px sólidas pretas
- **Botões:** Fundo preto, texto branco (invertem ao hover)
- **Inputs:** Bordas pretas, fundo branco
- **Mapa:** Tile layer em tons de cinza

## 🗺️ Funcionalidades do Mapa

### Upload de Dados
1. Selecione arquivo `.parquet` de lotes ou imóveis
2. Clique em "ENVIAR"
3. Dados são carregados automaticamente no mapa

### Visualização
- **Lotes:** Polígonos pretos com contorno
- **Imóveis:** Círculos cinza
- **Popups:** Clique nos elementos para ver detalhes

### Filtros
- **Por bairro:** Digite o nome do bairro
- **Limite:** Número máximo de resultados
- **Camadas:** Mostrar/ocultar lotes e imóveis

### Análise Espacial
1. Configure o raio em metros (100-10000)
2. Clique em qualquer ponto do mapa
3. Um círculo aparece mostrando a área de análise
4. Resultados aparecem no painel:
   - Número de lotes e imóveis na área
   - Estatísticas (área média, preço médio, etc.)

## 📊 Formatos de Dados

### Lotes (.parquet)
```
Colunas: codLote, logradouro, numero, bairro, sigla_trat,
area_terreno, ca, to, limite_altura, afast_frontal,
limite_embasamento, gabarito, altura, geometry,
inscricaoImobiliaria, tipoConstrucao, numeroPavimentos, ocupacao
```

### Imóveis (.parquet)
```
Colunas: Incorporador, Empreendimento, Bairro, Endereco, Cidade,
Dormitorios, Metragem Privativa, Vagas, Preco Total, Status,
Unidades Total, Unidades Vendidas, Estoque Atual, geometry (opcional)
```

## 🔌 API Endpoints

Todos os endpoints da API estão disponíveis e documentados em `/api-docs`:

- `GET /` - Frontend principal
- `GET /stats-page` - Página de estatísticas
- `GET /api-docs` - Documentação
- `GET /health` - Health check API
- `POST /upload/lotes` - Upload de lotes
- `POST /upload/imoveis` - Upload de imóveis
- `GET /stats` - Estatísticas JSON
- `GET /lotes/geojson` - Lotes em GeoJSON
- `GET /imoveis/geojson` - Imóveis em GeoJSON
- `GET /bounds` - Limites geográficos
- `POST /analyze` - Análise espacial

## 🧪 Testes

### Testar manualmente

1. **Verificar se o servidor está rodando:**
```bash
curl http://localhost:8000/health
```

2. **Testar upload (com arquivo exemplo):**
```bash
curl -X POST http://localhost:8000/upload/lotes \
  -F "file=@lotes.parquet"
```

3. **Ver estatísticas:**
```bash
curl http://localhost:8000/stats
```

4. **Testar análise espacial:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"latitude": -20.3155, "longitude": -40.3128, "radius_meters": 1000}'
```

### Script de testes automatizado
```bash
python test_api.py
```

## 🐳 Docker

### Executar com Docker Compose

```bash
docker-compose -f docker-compose-flask.yml up --build
```

O frontend estará disponível em http://localhost:8000

## 🛠️ Desenvolvimento

### Estrutura do código

**Templates (Jinja2):**
- `base.html` - Layout base com header, footer, imports
- `index.html` - Extends base, conteúdo da página principal
- `stats.html` - Página de estatísticas
- `api_docs.html` - Documentação da API

**JavaScript:**
- Funções assíncronas com `fetch()` para chamadas à API
- Leaflet para renderização do mapa
- Event listeners para interatividade

**CSS:**
- Mobile-first com media queries
- Grid layout para responsividade
- Variáveis CSS para consistência

### Modificar o frontend

1. **Editar templates:** `templates/*.html`
2. **Editar estilos:** `static/css/style.css`
3. **Editar lógica:** `static/js/app.js`
4. Recarregue a página (Ctrl+F5 para limpar cache)

### Adicionar nova página

1. Criar template em `templates/nova_pagina.html`:
```html
{% extends "base.html" %}
{% block content %}
  <h1>Nova Página</h1>
{% endblock %}
```

2. Adicionar rota em `app.py`:
```python
@app.route("/nova-pagina")
def nova_pagina():
    return render_template('nova_pagina.html')
```

## 📦 Dependências

```
Flask==3.0.0           # Framework web
flask-cors==4.0.0      # CORS support
Werkzeug==3.0.1        # WSGI utilities
pandas==2.1.4          # Data manipulation
geopandas==0.14.2      # Geospatial data
shapely==2.0.2         # Geometric operations
pyarrow==14.0.2        # Parquet support
numpy==1.26.3          # Numerical computing
gunicorn==21.2.0       # Production server
```

## 🔍 Troubleshooting

### Problema: CSS/JS não carrega
**Solução:** Verifique se os arquivos estão em `static/` e use `url_for()`:
```html
<link href="{{ url_for('static', filename='css/style.css') }}">
```

### Problema: Mapa não aparece
**Solução:**
- Verifique o console do navegador (F12)
- Confirme que Leaflet está carregando
- Verifique permissões de CORS

### Problema: Upload falha
**Solução:**
- Verifique se o arquivo é `.parquet`
- Confirme que as colunas esperadas existem
- Veja os logs do Flask no terminal

### Problema: 404 em templates
**Solução:**
- Verifique se `templates/` está no mesmo nível de `app.py`
- Confirme que os nomes dos arquivos estão corretos

## 📝 Convenções

### Código Python
- PEP 8 style guide
- Type hints quando possível
- Docstrings em português

### Templates
- Identação: 2 espaços
- Nomes de arquivos: snake_case.html
- Blocos Jinja2: `{% block %}` com espaços

### JavaScript
- ES6+ syntax
- async/await para chamadas assíncronas
- Comentários em português

### CSS
- BEM-like naming
- Mobile-first
- Variáveis CSS para cores e espaçamentos

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: Adicionar nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

---

Desenvolvido com ⚫⚪ (preto e branco) usando Flask + Jinja2 + Leaflet
