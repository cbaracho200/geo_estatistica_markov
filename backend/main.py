from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import tempfile
import os
from datetime import datetime
from typing import Optional

from models import (
    AnalysisRequest,
    AnalysisResponse,
    UploadResponse,
    HealthResponse
)
from spatial_engine import SpatialEngine

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Geoestatística Imobiliária",
    description="API para análise espacial de dados imobiliários",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Motor de análise espacial (singleton)
spatial_engine = SpatialEngine()


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="online",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check detalhado"""
    return HealthResponse(
        status="online",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/upload/lotes", response_model=UploadResponse)
async def upload_lotes(file: UploadFile = File(...)):
    """
    Upload de arquivo Parquet com dados de lotes de Vitória

    Colunas esperadas: codLote, logradouro, numero, bairro, sigla_trat,
    area_terreno, ca, to, limite_altura, afast_frontal, limite_embasamento,
    gabarito, altura, geometry, inscricaoImobiliaria, tipoConstrucao,
    numeroPavimentos, ocupacao
    """
    if not file.filename.endswith('.parquet'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .parquet")

    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Carregar no motor espacial
        count = spatial_engine.load_parquet_lotes(tmp_path)

        # Ler colunas do arquivo
        df = pd.read_parquet(tmp_path)
        columns = df.columns.tolist()

        # Limpar arquivo temporário
        os.unlink(tmp_path)

        return UploadResponse(
            message=f"Lotes carregados com sucesso",
            records_count=count,
            file_type="lotes",
            columns=columns
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@app.post("/upload/imoveis", response_model=UploadResponse)
async def upload_imoveis(file: UploadFile = File(...)):
    """
    Upload de arquivo Parquet com dados de imóveis

    Colunas esperadas: Incorporador, Empreendimento, Bairro, Endereco, Cidade,
    Dormitorios, Metragem Privativa, Vagas, Preco Total, Status,
    Unidades Total, Unidades Vendidas, Estoque Atual
    """
    if not file.filename.endswith('.parquet'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .parquet")

    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Carregar no motor espacial
        count = spatial_engine.load_parquet_imoveis(tmp_path)

        # Ler colunas do arquivo
        df = pd.read_parquet(tmp_path)
        columns = df.columns.tolist()

        # Limpar arquivo temporário
        os.unlink(tmp_path)

        return UploadResponse(
            message=f"Imóveis carregados com sucesso",
            records_count=count,
            file_type="imoveis",
            columns=columns
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_area(request: AnalysisRequest):
    """
    Analisa uma área circular ao redor de um ponto

    Retorna lotes e imóveis dentro do raio especificado
    """
    try:
        result = spatial_engine.analyze_radius(
            lat=request.latitude,
            lon=request.longitude,
            radius_meters=request.radius_meters,
            filters=request.filters
        )

        return AnalysisResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.get("/lotes/geojson")
async def get_lotes_geojson(
    bairro: Optional[str] = Query(None, description="Filtrar por bairro"),
    limit: Optional[int] = Query(1000, description="Limite de resultados")
):
    """Retorna todos os lotes em formato GeoJSON"""
    try:
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

        return JSONResponse(content=geojson)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lotes: {str(e)}")


@app.get("/imoveis/geojson")
async def get_imoveis_geojson(
    bairro: Optional[str] = Query(None, description="Filtrar por bairro"),
    limit: Optional[int] = Query(1000, description="Limite de resultados")
):
    """Retorna todos os imóveis em formato GeoJSON"""
    try:
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

        return JSONResponse(content=geojson)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar imóveis: {str(e)}")


@app.get("/bounds")
async def get_bounds():
    """Retorna os limites geográficos dos dados carregados"""
    try:
        bounds = spatial_engine.get_bounds()

        if bounds is None:
            return JSONResponse(content={
                "message": "Nenhum dado carregado ainda",
                "bounds": None
            })

        return JSONResponse(content={
            "bounds": {
                "minLng": bounds[0],
                "minLat": bounds[1],
                "maxLng": bounds[2],
                "maxLat": bounds[3]
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar limites: {str(e)}")


@app.get("/stats")
async def get_statistics():
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

        return JSONResponse(content=stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular estatísticas: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
