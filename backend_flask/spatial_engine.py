import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import unary_union
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json


class SpatialEngine:
    """Motor de análise geoespacial para dados imobiliários"""

    def __init__(self):
        self.lotes_gdf: Optional[gpd.GeoDataFrame] = None
        self.imoveis_gdf: Optional[gpd.GeoDataFrame] = None
        self.crs = "EPSG:4326"  # WGS84

    def load_parquet_lotes(self, file_path: str) -> int:
        """Carrega dados de lotes de arquivo Parquet"""
        df = pd.read_parquet(file_path)

        # Converter coluna geometry se for string
        if 'geometry' in df.columns and isinstance(df['geometry'].iloc[0], str):
            df['geometry'] = df['geometry'].apply(lambda x: shape(json.loads(x)) if pd.notna(x) else None)
        elif 'geometry' in df.columns and isinstance(df['geometry'].iloc[0], dict):
            df['geometry'] = df['geometry'].apply(lambda x: shape(x) if pd.notna(x) else None)

        self.lotes_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=self.crs)
        return len(self.lotes_gdf)

    def load_parquet_imoveis(self, file_path: str) -> int:
        """Carrega dados de imóveis de arquivo Parquet"""
        df = pd.read_parquet(file_path)

        # Se não houver geometria, tentar geocodificar baseado em endereço
        if 'geometry' not in df.columns:
            # Por enquanto, criar geometria vazia
            df['geometry'] = None
        else:
            # Converter coluna geometry se for string ou dict
            if isinstance(df['geometry'].iloc[0], str):
                df['geometry'] = df['geometry'].apply(lambda x: shape(json.loads(x)) if pd.notna(x) else None)
            elif isinstance(df['geometry'].iloc[0], dict):
                df['geometry'] = df['geometry'].apply(lambda x: shape(x) if pd.notna(x) else None)

        self.imoveis_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=self.crs)
        return len(self.imoveis_gdf)

    def add_lotes_from_dataframe(self, df: pd.DataFrame) -> int:
        """Adiciona lotes de um DataFrame"""
        if 'geometry' in df.columns:
            if isinstance(df['geometry'].iloc[0], (str, dict)):
                df['geometry'] = df['geometry'].apply(
                    lambda x: shape(json.loads(x) if isinstance(x, str) else x) if pd.notna(x) else None
                )

        new_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=self.crs)

        if self.lotes_gdf is None:
            self.lotes_gdf = new_gdf
        else:
            self.lotes_gdf = pd.concat([self.lotes_gdf, new_gdf], ignore_index=True)

        return len(new_gdf)

    def add_imoveis_from_dataframe(self, df: pd.DataFrame) -> int:
        """Adiciona imóveis de um DataFrame"""
        if 'geometry' not in df.columns:
            df['geometry'] = None
        elif isinstance(df['geometry'].iloc[0], (str, dict)):
            df['geometry'] = df['geometry'].apply(
                lambda x: shape(json.loads(x) if isinstance(x, str) else x) if pd.notna(x) else None
            )

        new_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=self.crs)

        if self.imoveis_gdf is None:
            self.imoveis_gdf = new_gdf
        else:
            self.imoveis_gdf = pd.concat([self.imoveis_gdf, new_gdf], ignore_index=True)

        return len(new_gdf)

    def analyze_radius(
        self,
        lat: float,
        lon: float,
        radius_meters: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analisa uma área circular ao redor de um ponto"""

        # Criar ponto central
        point = Point(lon, lat)

        # Criar buffer (aproximação em graus)
        # 1 grau ~ 111km, então convertemos metros para graus
        radius_degrees = radius_meters / 111000
        buffer = point.buffer(radius_degrees)

        # Filtrar lotes dentro do raio
        lotes_nearby = []
        if self.lotes_gdf is not None and len(self.lotes_gdf) > 0:
            lotes_mask = self.lotes_gdf.geometry.intersects(buffer)
            lotes_filtered = self.lotes_gdf[lotes_mask].copy()

            # Aplicar filtros adicionais
            if filters:
                for key, value in filters.items():
                    if key in lotes_filtered.columns:
                        lotes_filtered = lotes_filtered[lotes_filtered[key] == value]

            lotes_nearby = self._geodataframe_to_geojson(lotes_filtered)

        # Filtrar imóveis dentro do raio
        imoveis_nearby = []
        if self.imoveis_gdf is not None and len(self.imoveis_gdf) > 0:
            imoveis_mask = self.imoveis_gdf.geometry.notna() & self.imoveis_gdf.geometry.intersects(buffer)
            imoveis_filtered = self.imoveis_gdf[imoveis_mask].copy()

            # Aplicar filtros adicionais
            if filters:
                for key, value in filters.items():
                    if key in imoveis_filtered.columns:
                        imoveis_filtered = imoveis_filtered[imoveis_filtered[key] == value]

            imoveis_nearby = self._geodataframe_to_geojson(imoveis_filtered)

        # Calcular estatísticas
        stats = self._calculate_statistics(lotes_nearby, imoveis_nearby)

        return {
            'point': {'latitude': lat, 'longitude': lon},
            'radius_meters': radius_meters,
            'lotes_encontrados': len(lotes_nearby),
            'imoveis_encontrados': len(imoveis_nearby),
            'estatisticas': stats,
            'lotes': lotes_nearby,
            'imoveis': imoveis_nearby
        }

    def _geodataframe_to_geojson(self, gdf: gpd.GeoDataFrame) -> List[Dict[str, Any]]:
        """Converte GeoDataFrame para lista de features GeoJSON"""
        features = []
        for idx, row in gdf.iterrows():
            properties = row.drop('geometry').to_dict()

            # Converter valores numpy para tipos nativos Python
            for key, value in properties.items():
                if isinstance(value, (np.integer, np.floating)):
                    properties[key] = float(value) if isinstance(value, np.floating) else int(value)
                elif pd.isna(value):
                    properties[key] = None

            feature = {
                'type': 'Feature',
                'properties': properties,
                'geometry': json.loads(gpd.GeoSeries([row.geometry]).to_json())['features'][0]['geometry'] if row.geometry else None
            }
            features.append(feature)

        return features

    def _calculate_statistics(self, lotes: List[Dict], imoveis: List[Dict]) -> Dict[str, Any]:
        """Calcula estatísticas dos dados encontrados"""
        stats = {
            'lotes': {},
            'imoveis': {}
        }

        # Estatísticas de lotes
        if lotes:
            areas = [l['properties'].get('area_terreno') for l in lotes if l['properties'].get('area_terreno')]
            if areas:
                stats['lotes']['area_media'] = float(np.mean(areas))
                stats['lotes']['area_total'] = float(np.sum(areas))
                stats['lotes']['area_min'] = float(np.min(areas))
                stats['lotes']['area_max'] = float(np.max(areas))

            bairros = [l['properties'].get('bairro') for l in lotes if l['properties'].get('bairro')]
            if bairros:
                stats['lotes']['bairros_unicos'] = len(set(bairros))
                stats['lotes']['distribuicao_bairros'] = dict(pd.Series(bairros).value_counts())

        # Estatísticas de imóveis
        if imoveis:
            precos = [i['properties'].get('preco_total') for i in imoveis if i['properties'].get('preco_total')]
            if precos:
                stats['imoveis']['preco_medio'] = float(np.mean(precos))
                stats['imoveis']['preco_min'] = float(np.min(precos))
                stats['imoveis']['preco_max'] = float(np.max(precos))

            metragens = [i['properties'].get('metragem_privativa') for i in imoveis if i['properties'].get('metragem_privativa')]
            if metragens:
                stats['imoveis']['metragem_media'] = float(np.mean(metragens))

            dormitorios = [i['properties'].get('dormitorios') for i in imoveis if i['properties'].get('dormitorios')]
            if dormitorios:
                stats['imoveis']['distribuicao_dormitorios'] = dict(pd.Series(dormitorios).value_counts())

        return stats

    def get_all_lotes_geojson(self) -> Dict[str, Any]:
        """Retorna todos os lotes em formato GeoJSON"""
        if self.lotes_gdf is None or len(self.lotes_gdf) == 0:
            return {'type': 'FeatureCollection', 'features': []}

        return {
            'type': 'FeatureCollection',
            'features': self._geodataframe_to_geojson(self.lotes_gdf)
        }

    def get_all_imoveis_geojson(self) -> Dict[str, Any]:
        """Retorna todos os imóveis em formato GeoJSON"""
        if self.imoveis_gdf is None or len(self.imoveis_gdf) == 0:
            return {'type': 'FeatureCollection', 'features': []}

        return {
            'type': 'FeatureCollection',
            'features': self._geodataframe_to_geojson(self.imoveis_gdf)
        }

    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Retorna os limites geográficos dos dados (minx, miny, maxx, maxy)"""
        bounds = []

        if self.lotes_gdf is not None and len(self.lotes_gdf) > 0:
            bounds.append(self.lotes_gdf.total_bounds)

        if self.imoveis_gdf is not None and len(self.imoveis_gdf) > 0:
            valid_geoms = self.imoveis_gdf[self.imoveis_gdf.geometry.notna()]
            if len(valid_geoms) > 0:
                bounds.append(valid_geoms.total_bounds)

        if not bounds:
            return None

        # Combinar bounds
        all_bounds = np.array(bounds)
        return (
            float(all_bounds[:, 0].min()),  # minx
            float(all_bounds[:, 1].min()),  # miny
            float(all_bounds[:, 2].max()),  # maxx
            float(all_bounds[:, 3].max())   # maxy
        )
