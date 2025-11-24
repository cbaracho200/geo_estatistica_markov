from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError
import pandas as pd
import tempfile
import os
from datetime import datetime
from typing import Optional

from spatial_engine import SpatialEngine

# Inicializar Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Motor de análise espacial (singleton)
spatial_engine = SpatialEngine()


@app.route("/", methods=["GET"])
def root():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check detalhado"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route("/upload/lotes", methods=["POST"])
def upload_lotes():
    """
    Upload de arquivo Parquet com dados de lotes de Vitória

    Colunas esperadas: codLote, logradouro, numero, bairro, sigla_trat,
    area_terreno, ca, to, limite_altura, afast_frontal, limite_embasamento,
    gabarito, altura, geometry, inscricaoImobiliaria, tipoConstrucao,
    numeroPavimentos, ocupacao
    """
    if 'file' not in request.files:
        return jsonify({"detail": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"detail": "Nenhum arquivo selecionado"}), 400

    if not file.filename.endswith('.parquet'):
        return jsonify({"detail": "Arquivo deve ser .parquet"}), 400

    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Carregar no motor espacial
        count = spatial_engine.load_parquet_lotes(tmp_path)

        # Ler colunas do arquivo
        df = pd.read_parquet(tmp_path)
        columns = df.columns.tolist()

        # Limpar arquivo temporário
        os.unlink(tmp_path)

        return jsonify({
            "message": "Lotes carregados com sucesso",
            "records_count": count,
            "file_type": "lotes",
            "columns": columns
        })

    except Exception as e:
        return jsonify({"detail": f"Erro ao processar arquivo: {str(e)}"}), 500


@app.route("/upload/imoveis", methods=["POST"])
def upload_imoveis():
    """
    Upload de arquivo Parquet com dados de imóveis

    Colunas esperadas: Incorporador, Empreendimento, Bairro, Endereco, Cidade,
    Dormitorios, Metragem Privativa, Vagas, Preco Total, Status,
    Unidades Total, Unidades Vendidas, Estoque Atual
    """
    if 'file' not in request.files:
        return jsonify({"detail": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"detail": "Nenhum arquivo selecionado"}), 400

    if not file.filename.endswith('.parquet'):
        return jsonify({"detail": "Arquivo deve ser .parquet"}), 400

    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Carregar no motor espacial
        count = spatial_engine.load_parquet_imoveis(tmp_path)

        # Ler colunas do arquivo
        df = pd.read_parquet(tmp_path)
        columns = df.columns.tolist()

        # Limpar arquivo temporário
        os.unlink(tmp_path)

        return jsonify({
            "message": "Imóveis carregados com sucesso",
            "records_count": count,
            "file_type": "imoveis",
            "columns": columns
        })

    except Exception as e:
        return jsonify({"detail": f"Erro ao processar arquivo: {str(e)}"}), 500


@app.route("/analyze", methods=["POST"])
def analyze_area():
    """
    Analisa uma área circular ao redor de um ponto

    Retorna lotes e imóveis dentro do raio especificado
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"detail": "Dados inválidos"}), 400

        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius_meters = data.get('radius_meters', 1000)
        filters = data.get('filters')

        if latitude is None or longitude is None:
            return jsonify({"detail": "latitude e longitude são obrigatórios"}), 400

        result = spatial_engine.analyze_radius(
            lat=latitude,
            lon=longitude,
            radius_meters=radius_meters,
            filters=filters
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"detail": f"Erro na análise: {str(e)}"}), 500


@app.route("/lotes/geojson", methods=["GET"])
def get_lotes_geojson():
    """Retorna todos os lotes em formato GeoJSON"""
    try:
        bairro = request.args.get('bairro')
        limit = request.args.get('limit', 1000, type=int)

        geojson = spatial_engine.get_all_lotes_geojson()

        # Aplicar filtros se necessário
        if bairro:
            geojson['features'] = [
                f for f in geojson['features']
                if f['properties'].get('bairro') == bairro
            ]

        # Limitar resultados
        if limit:
            geojson['features'] = geojson['features'][:limit]

        return jsonify(geojson)

    except Exception as e:
        return jsonify({"detail": f"Erro ao buscar lotes: {str(e)}"}), 500


@app.route("/imoveis/geojson", methods=["GET"])
def get_imoveis_geojson():
    """Retorna todos os imóveis em formato GeoJSON"""
    try:
        bairro = request.args.get('bairro')
        limit = request.args.get('limit', 1000, type=int)

        geojson = spatial_engine.get_all_imoveis_geojson()

        # Aplicar filtros se necessário
        if bairro:
            geojson['features'] = [
                f for f in geojson['features']
                if f['properties'].get('bairro') == bairro
            ]

        # Limitar resultados
        if limit:
            geojson['features'] = geojson['features'][:limit]

        return jsonify(geojson)

    except Exception as e:
        return jsonify({"detail": f"Erro ao buscar imóveis: {str(e)}"}), 500


@app.route("/bounds", methods=["GET"])
def get_bounds():
    """Retorna os limites geográficos dos dados carregados"""
    try:
        bounds = spatial_engine.get_bounds()

        if bounds is None:
            return jsonify({
                "message": "Nenhum dado carregado ainda",
                "bounds": None
            })

        return jsonify({
            "bounds": {
                "minLng": bounds[0],
                "minLat": bounds[1],
                "maxLng": bounds[2],
                "maxLat": bounds[3]
            }
        })

    except Exception as e:
        return jsonify({"detail": f"Erro ao buscar limites: {str(e)}"}), 500


@app.route("/stats", methods=["GET"])
def get_statistics():
    """Retorna estatísticas gerais dos dados carregados"""
    try:
        stats = {
            "lotes": {
                "total": len(spatial_engine.lotes_gdf) if spatial_engine.lotes_gdf is not None else 0,
                "com_geometria": len(spatial_engine.lotes_gdf[spatial_engine.lotes_gdf.geometry.notna()]) if spatial_engine.lotes_gdf is not None else 0
            },
            "imoveis": {
                "total": len(spatial_engine.imoveis_gdf) if spatial_engine.imoveis_gdf is not None else 0,
                "com_geometria": len(spatial_engine.imoveis_gdf[spatial_engine.imoveis_gdf.geometry.notna()]) if spatial_engine.imoveis_gdf is not None else 0
            }
        }

        # Adicionar bairros únicos
        if spatial_engine.lotes_gdf is not None and len(spatial_engine.lotes_gdf) > 0:
            stats['lotes']['bairros_unicos'] = spatial_engine.lotes_gdf['bairro'].nunique() if 'bairro' in spatial_engine.lotes_gdf.columns else 0

        if spatial_engine.imoveis_gdf is not None and len(spatial_engine.imoveis_gdf) > 0:
            stats['imoveis']['bairros_unicos'] = spatial_engine.imoveis_gdf['bairro'].nunique() if 'bairro' in spatial_engine.imoveis_gdf.columns else 0

        return jsonify(stats)

    except Exception as e:
        return jsonify({"detail": f"Erro ao calcular estatísticas: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"detail": "Rota não encontrada"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"detail": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
