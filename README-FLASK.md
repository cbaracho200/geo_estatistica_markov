# Sistema de Geoestatística Imobiliária - Versão Flask

Sistema completo de análise espacial de dados imobiliários com Flask framework, design minimalista em preto e branco.

## 📋 Diferenças entre FastAPI e Flask

Este projeto oferece duas versões do backend:

| Característica | FastAPI (backend/) | Flask (backend_flask/) |
|---|---|---|
| Framework | FastAPI | Flask |
| Servidor | Uvicorn | Gunicorn |
| Documentação API | Swagger/OpenAPI automático | Manual |
| Validação de dados | Pydantic | Manual |
| Performance | Assíncrono (async/await) | Síncrono |
| Complexidade | Maior | Menor |

## 🏗️ Arquitetura da Versão Flask

```
geo_estatistica_markov/
│
├── backend_flask/           # Flask Backend
│   ├── app.py              # Aplicação Flask principal
│   ├── spatial_engine.py   # Motor de análise espacial
│   ├── requirements.txt    # Dependências Python
│   └── Dockerfile          # Container backend Flask
│
├── frontend/               # React + TypeScript Frontend
│   └── (mesma estrutura)
│
├── docker-compose-flask.yml # Setup completo com Flask
└── README-FLASK.md         # Este arquivo
```

## 🚀 Início Rápido com Flask

### Pré-requisitos

- Docker e Docker Compose
- Git
- Python 3.11+ (para desenvolvimento local)

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

3. **Inicie os containers com Flask:**
```bash
docker-compose -f docker-compose-flask.yml up --build
```

4. **Acesse a aplicação:**
- Frontend: http://localhost:3000
- Backend API Flask: http://localhost:8000
- Health check: http://localhost:8000/health

## 🛠️ Desenvolvimento Local (sem Docker)

### Backend Flask

**Executar localmente:**
```bash
cd backend_flask
pip install -r requirements.txt

# Desenvolvimento (com auto-reload)
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000 --reload

# Ou com Python diretamente
python app.py

# Produção (com gunicorn)
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
```

**Tecnologias:**
- Flask 3.0
- Flask-CORS
- GeoPandas
- Shapely
- Pandas
- PyArrow (Parquet)
- Gunicorn

### Frontend

**Executar localmente:**
```bash
cd frontend
npm install
npm run dev
```

## 🔌 API Endpoints Flask

Todos os endpoints são os mesmos da versão FastAPI:

### Health Check
```
GET /
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

## 📊 Testando a API Flask

### Usando curl

**Health check:**
```bash
curl http://localhost:8000/health
```

**Upload de lotes:**
```bash
curl -X POST http://localhost:8000/upload/lotes \
  -F "file=@/path/to/lotes.parquet"
```

**Análise espacial:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -20.3155,
    "longitude": -40.3128,
    "radius_meters": 1000
  }'
```

**Obter estatísticas:**
```bash
curl http://localhost:8000/stats
```

### Usando Python requests

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Upload de arquivo
files = {'file': open('lotes.parquet', 'rb')}
response = requests.post('http://localhost:8000/upload/lotes', files=files)
print(response.json())

# Análise espacial
data = {
    "latitude": -20.3155,
    "longitude": -40.3128,
    "radius_meters": 1000
}
response = requests.post('http://localhost:8000/analyze', json=data)
print(response.json())
```

## 📦 Produção

### Build do Frontend
```bash
cd frontend
npm run build
```

### Deploy com Docker (Flask)
```bash
docker-compose -f docker-compose-flask.yml up -d
```

### Deploy manual do Flask

1. **Instalar dependências:**
```bash
cd backend_flask
pip install -r requirements.txt
```

2. **Executar com gunicorn (produção):**
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
```

3. **Configurar nginx (opcional):**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔍 Comparação de Performance

### FastAPI (Assíncrono)
- ✅ Melhor para operações I/O intensivas
- ✅ Suporta requisições concorrentes
- ✅ Performance superior sob alta carga
- ❌ Mais complexo para iniciantes

### Flask (Síncrono)
- ✅ Mais simples e direto
- ✅ Ampla comunidade e documentação
- ✅ Mais fácil de debugar
- ✅ Adequado para cargas médias
- ❌ Performance inferior em alta concorrência

## 🧪 Testes

### Testar Backend Flask
```bash
cd backend_flask
pytest  # (necessário criar testes)
```

### Testar endpoints manualmente
```bash
# Instalar httpie
pip install httpie

# Health check
http GET localhost:8000/health

# Stats
http GET localhost:8000/stats

# Upload
http POST localhost:8000/upload/lotes file@lotes.parquet
```

## 🐛 Debug

### Habilitar debug mode
```bash
export FLASK_DEBUG=1
flask run
```

### Ver logs do Docker
```bash
docker-compose -f docker-compose-flask.yml logs -f backend-flask
```

### Modo debug no código
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

## 📚 Estrutura de Código Flask

### app.py
```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/endpoint', methods=['GET', 'POST'])
def endpoint():
    # Lógica do endpoint
    return jsonify({"result": "data"})
```

### Tratamento de erros
```python
@app.errorhandler(404)
def not_found(e):
    return jsonify({"detail": "Não encontrado"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"detail": "Erro interno"}), 500
```

## 🔄 Migração de FastAPI para Flask

Se você está migrando de FastAPI para Flask:

1. ✅ Não precisa reescrever spatial_engine.py (independente)
2. ✅ Frontend continua igual (mesma API REST)
3. ✅ Substituir `@app.get()` por `@app.route(methods=['GET'])`
4. ✅ Substituir `UploadFile` por `request.files`
5. ✅ Substituir `Query()` por `request.args.get()`
6. ✅ Remover `async/await` (Flask é síncrono)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🔗 Links Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [GeoPandas Documentation](https://geopandas.org/)
- [GeoJSON Specification](https://geojson.org/)

## 📞 Suporte

Para questões e suporte, abra uma issue no GitHub.

---

Desenvolvido com ⚫⚪ (preto e branco) usando Flask
