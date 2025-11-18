from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LoteVitoria(BaseModel):
    """Modelo para dados de lotes de Vitória"""
    codLote: str
    logradouro: str
    numero: Optional[str] = None
    bairro: str
    sigla_trat: Optional[str] = None
    area_terreno: Optional[float] = None
    ca: Optional[float] = None  # Coeficiente de Aproveitamento
    to: Optional[float] = None  # Taxa de Ocupação
    limite_altura: Optional[float] = None
    afast_frontal: Optional[float] = None
    limite_embasamento: Optional[float] = None
    gabarito: Optional[str] = None
    altura: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON geometry
    inscricaoImobiliaria: Optional[str] = None
    tipoConstrucao: Optional[str] = None
    numeroPavimentos: Optional[int] = None
    ocupacao: Optional[str] = None


class Imovel(BaseModel):
    """Modelo para dados de imóveis"""
    incorporador: str
    empreendimento: str
    bairro: str
    endereco: str
    cidade: str
    dormitorios: Optional[int] = None
    metragem_privativa: Optional[float] = Field(None, alias="Metragem Privativa")
    vagas: Optional[int] = None
    preco_total: Optional[float] = Field(None, alias="Preco Total")
    status: Optional[str] = None
    unidades_total: Optional[int] = Field(None, alias="Unidades Total")
    unidades_vendidas: Optional[int] = Field(None, alias="Unidades Vendidas")
    estoque_atual: Optional[int] = Field(None, alias="Estoque Atual")
    geometry: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class AnalysisRequest(BaseModel):
    """Requisição para análise espacial"""
    latitude: float
    longitude: float
    radius_meters: float = 1000
    filters: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Resposta da análise espacial"""
    point: Dict[str, float]
    radius_meters: float
    lotes_encontrados: int
    imoveis_encontrados: int
    estatisticas: Dict[str, Any]
    lotes: List[Dict[str, Any]]
    imoveis: List[Dict[str, Any]]


class UploadResponse(BaseModel):
    """Resposta do upload de arquivo"""
    message: str
    records_count: int
    file_type: str
    columns: List[str]


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str
    timestamp: str
    version: str
