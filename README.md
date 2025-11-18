# Sistema de Geoestatística Imobiliária

Sistema completo de análise espacial de dados imobiliários com design minimalista em preto e branco.

## 🏗️ Arquitetura

```
geo_estatistica_markov/
│
├── backend/                 # FastAPI Backend
│   ├── main.py             # Rotas da API
│   ├── spatial_engine.py   # Motor de análise espacial
│   ├── models.py           # Modelos de dados
│   ├── requirements.txt    # Dependências Python
│   └── Dockerfile          # Container backend
│
├── frontend/               # React + TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx        # Componente principal
│   │   ├── Map.tsx        # Mapa interativo (Leaflet)
│   │   ├── api.ts         # Cliente API
│   │   ├── App.css        # Design minimalista
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile         # Container frontend
│
├── data/                   # Arquivos de dados
│   └── sample_properties.geojson
│
├── docker-compose.yml      # Setup completo
├── .env.example           # Variáveis de ambiente
└── README.md
```

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Git

### Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd geo_estatistica_markov
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
```

3. **Inicie os containers:**
```bash
docker-compose up --build
```

4. **Acesse a aplicação:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## 📊 Formato dos Dados

### Lotes de Vitória (Parquet)

Colunas esperadas:
- `codLote`: Código do lote
- `logradouro`: Nome da rua
- `numero`: Número do imóvel
- `bairro`: Bairro
- `sigla_trat`: Sigla do tratamento urbanístico
- `area_terreno`: Área do terreno em m²
- `ca`: Coeficiente de Aproveitamento
- `to`: Taxa de Ocupação
- `limite_altura`: Limite de altura
- `afast_frontal`: Afastamento frontal
- `limite_embasamento`: Limite de embasamento
- `gabarito`: Gabarito
- `altura`: Altura
- `geometry`: Geometria (GeoJSON format)
- `inscricaoImobiliaria`: Inscrição Imobiliária
- `tipoConstrucao`: Tipo de construção
- `numeroPavimentos`: Número de pavimentos
- `ocupacao`: Ocupação

### Imóveis (Parquet)

Colunas esperadas:
- `Incorporador`: Nome do incorporador
- `Empreendimento`: Nome do empreendimento
- `Bairro`: Bairro
- `Endereco`: Endereço completo
- `Cidade`: Cidade
- `Dormitorios`: Número de dormitórios
- `Metragem Privativa`: Área privativa em m²
- `Vagas`: Número de vagas de garagem
- `Preco Total`: Preço total
- `Status`: Status do imóvel
- `Unidades Total`: Total de unidades
- `Unidades Vendidas`: Unidades vendidas
- `Estoque Atual`: Estoque atual

**Nota:** A coluna `geometry` é opcional para imóveis. Se não fornecida, o sistema pode geocodificar baseado no endereço (funcionalidade a ser implementada).

## 🎨 Design

O sistema utiliza um design minimalista em preto e branco:
- Cores principais: #000000 (preto) e #FFFFFF (branco)
- Tipografia: Courier New (monospace)
- Interface limpa e intuitiva
- Foco na visualização de dados

## 🗺️ Funcionalidades

### 1. Upload de Dados
- Importação de arquivos Parquet
- Validação automática de colunas
- Suporte para geometrias GeoJSON
- Feedback visual de progresso

### 2. Visualização Espacial
- Mapa interativo com Leaflet
- Camadas separadas para lotes e imóveis
- Popups informativos
- Ajuste automático de bounds

### 3. Análise Espacial
- Seleção de ponto no mapa
- Análise por raio (buffer circular)
- Estatísticas em tempo real
- Contagem de lotes e imóveis na área

### 4. Estatísticas
- Total de lotes e imóveis carregados
- Contagem com geometria válida
- Número de bairros únicos
- Métricas agregadas

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### Upload
```
POST /upload/lotes
POST /upload/imoveis
```
Body: multipart/form-data com arquivo .parquet

### Visualização
```
GET /lotes/geojson?bairro=Centro&limit=1000
GET /imoveis/geojson?bairro=Centro&limit=1000
GET /bounds
GET /stats
```

### Análise
```
POST /analyze
```
Body:
```json
{
  "latitude": -20.3155,
  "longitude": -40.3128,
  "radius_meters": 1000,
  "filters": {}
}
```

## 🛠️ Desenvolvimento

### Backend

**Executar localmente:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Tecnologias:**
- FastAPI
- GeoPandas
- Shapely
- Pandas
- PyArrow (Parquet)

### Frontend

**Executar localmente:**
```bash
cd frontend
npm install
npm run dev
```

**Tecnologias:**
- React 18
- TypeScript
- Leaflet / React-Leaflet
- Axios
- Vite

## 📦 Produção

### Build do Frontend
```bash
cd frontend
npm run build
```

### Deploy com Docker
```bash
docker-compose -f docker-compose.yml up -d
```

## 🧪 Testes

### Testar Backend
```bash
cd backend
pytest
```

### Testar Frontend
```bash
cd frontend
npm test
```

## 🔍 Estrutura de Dados Geográficos

O sistema suporta geometrias no formato GeoJSON:

```json
{
  "type": "Point",
  "coordinates": [-40.3128, -20.3155]
}
```

```json
{
  "type": "Polygon",
  "coordinates": [[
    [-40.31, -20.31],
    [-40.32, -20.31],
    [-40.32, -20.32],
    [-40.31, -20.32],
    [-40.31, -20.31]
  ]]
}
```

## 📝 Convenções

### Commit Messages
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes

### Branches
- `main`: Produção
- `develop`: Desenvolvimento
- `feature/*`: Novas funcionalidades
- `fix/*`: Correções

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Autores

Sistema desenvolvido para análise geoestatística de mercado imobiliário.

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Leaflet Documentation](https://leafletjs.com/)
- [GeoPandas Documentation](https://geopandas.org/)
- [GeoJSON Specification](https://geojson.org/)

## 📞 Suporte

Para questões e suporte, abra uma issue no GitHub.

---

Desenvolvido com ⚫⚪ (preto e branco)