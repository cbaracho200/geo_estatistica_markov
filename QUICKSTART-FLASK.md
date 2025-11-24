# 🚀 Guia de Início Rápido - Flask com Frontend Integrado

## O que foi criado?

Uma versão **completa e autocontida** do sistema usando **Flask** com frontend integrado:
- ✅ Backend Flask com todas as funcionalidades
- ✅ Frontend integrado usando templates Jinja2
- ✅ Design minimalista preto e branco
- ✅ Sem necessidade de React/Node.js
- ✅ Tudo roda em um único servidor Flask

## 🏃 Começar em 3 passos

### 1. Instalar dependências

```bash
cd backend_flask
pip install -r requirements.txt
```

### 2. Iniciar o servidor

**Desenvolvimento:**
```bash
python app.py
```

**Ou com Flask CLI:**
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000
```

### 3. Abrir no navegador

```
http://localhost:8000
```

Pronto! O sistema está rodando 🎉

## 📱 Páginas disponíveis

- **http://localhost:8000** - Mapa interativo principal
- **http://localhost:8000/stats-page** - Estatísticas
- **http://localhost:8000/api-docs** - Documentação da API
- **http://localhost:8000/health** - Health check (JSON)

## 🎯 Como usar

### 1. Upload de dados

Na página principal, na lateral esquerda:
1. Clique em "Escolher arquivo" em "Lotes" ou "Imóveis"
2. Selecione um arquivo `.parquet`
3. Clique em "ENVIAR LOTES" ou "ENVIAR IMÓVEIS"
4. Os dados aparecem automaticamente no mapa!

### 2. Visualizar no mapa

- **Lotes:** Polígonos pretos
- **Imóveis:** Círculos cinza
- **Clique** em qualquer elemento para ver detalhes

### 3. Filtrar dados

No painel lateral:
- Digite um bairro no campo "Filtrar por Bairro"
- Ajuste o "Limite de resultados"
- Use os checkboxes para mostrar/ocultar camadas
- Clique em "CARREGAR NO MAPA"

### 4. Análise espacial

1. Configure o raio em metros (campo "Raio")
2. Clique em qualquer ponto do mapa
3. Veja os resultados no painel "ANÁLISE ESPACIAL":
   - Número de lotes e imóveis na área
   - Estatísticas (área média, preço médio, etc.)

## 🎨 Design

O sistema usa um design **minimalista preto e branco**:
- Cores: apenas preto (#000000) e branco (#FFFFFF)
- Tipografia: Courier New (monospace)
- Bordas: 2px sólidas
- Botões: fundo preto, texto branco (invertem ao hover)

## 📊 Formato dos dados

### Lotes (.parquet)
Precisa ter estas colunas:
```
codLote, logradouro, numero, bairro, sigla_trat, area_terreno,
ca, to, limite_altura, afast_frontal, limite_embasamento,
gabarito, altura, geometry, inscricaoImobiliaria, tipoConstrucao,
numeroPavimentos, ocupacao
```

### Imóveis (.parquet)
Precisa ter estas colunas:
```
Incorporador, Empreendimento, Bairro, Endereco, Cidade,
Dormitorios, Metragem Privativa, Vagas, Preco Total, Status,
Unidades Total, Unidades Vendidas, Estoque Atual
```

A coluna `geometry` é opcional para imóveis.

## 🐳 Rodar com Docker

Se preferir usar Docker:

```bash
# Na raiz do projeto
docker-compose -f docker-compose-flask.yml up --build
```

Acesse: http://localhost:8000

## 🔧 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'flask'"
**Solução:**
```bash
cd backend_flask
pip install -r requirements.txt
```

### Problema: "Address already in use"
**Solução:** Outra aplicação está usando a porta 8000. Mude a porta:
```bash
python app.py  # Edite a última linha para usar outra porta
# ou
flask run --port=8001
```

### Problema: CSS não carrega
**Solução:** Limpe o cache do navegador (Ctrl+F5 ou Cmd+Shift+R)

### Problema: Mapa não aparece
**Solução:**
- Abra o console do navegador (F12)
- Verifique se há erros
- Confirme que tem conexão com internet (Leaflet usa CDN)

## 📚 Documentação completa

Para mais detalhes, veja:
- **backend_flask/README.md** - Documentação completa do frontend
- **README-FLASK.md** - Documentação da versão Flask
- **README.md** - Documentação geral do projeto

## 🆚 Diferenças entre FastAPI e Flask

| Característica | FastAPI (backend/) | Flask (backend_flask/) |
|---|---|---|
| Frontend | React separado | Integrado (Jinja2) |
| Complexidade | Maior | Menor |
| Documentação API | Swagger automático | Página manual |
| Performance | Assíncrono | Síncrono |
| Dependências | FastAPI + React + Node.js | Apenas Flask |

## 💡 Dicas

1. **Desenvolvimento:** Use `python app.py` para auto-reload
2. **Produção:** Use gunicorn: `gunicorn --bind 0.0.0.0:8000 --workers 4 app:app`
3. **Debug:** Abra o console do navegador (F12) para ver logs
4. **Performance:** Ajuste o "Limite de resultados" se o mapa ficar lento
5. **Dados grandes:** Use filtros por bairro para carregar menos dados

## 🎓 Próximos passos

1. **Teste a API** manualmente:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/stats
   ```

2. **Explore a documentação** em http://localhost:8000/api-docs

3. **Personalize o design** editando `static/css/style.css`

4. **Adicione funcionalidades** editando:
   - `templates/*.html` - Interface
   - `static/js/app.js` - Lógica
   - `app.py` - Backend

## ❓ Ajuda

Se tiver problemas:
1. Verifique os logs no terminal onde rodou `python app.py`
2. Abra o console do navegador (F12)
3. Consulte a documentação completa em `backend_flask/README.md`

---

Pronto para começar! Execute `python app.py` e abra http://localhost:8000 🚀
