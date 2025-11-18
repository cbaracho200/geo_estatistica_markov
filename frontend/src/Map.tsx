import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Circle, Popup, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { GeoJSONCollection, AnalysisResponse } from './api';

// Fix Leaflet default marker icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapProps {
  lotes: GeoJSONCollection | null;
  imoveis: GeoJSONCollection | null;
  analysisResult: AnalysisResponse | null;
  onMapClick?: (lat: number, lng: number) => void;
  center?: [number, number];
}

// Componente para capturar cliques no mapa
const MapClickHandler: React.FC<{ onClick: (lat: number, lng: number) => void }> = ({ onClick }) => {
  useMapEvents({
    click: (e) => {
      onClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

// Componente para ajustar o bounds do mapa
const FitBounds: React.FC<{ bounds: L.LatLngBoundsExpression | null }> = ({ bounds }) => {
  const map = useMap();

  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);

  return null;
};

const Map: React.FC<MapProps> = ({ lotes, imoveis, analysisResult, onMapClick, center }) => {
  const [mapCenter, setMapCenter] = useState<[number, number]>(center || [-20.3155, -40.3128]); // Vitória, ES
  const [mapZoom, setMapZoom] = useState(13);
  const [bounds, setBounds] = useState<L.LatLngBoundsExpression | null>(null);

  // Atualizar bounds quando os dados mudarem
  useEffect(() => {
    const allFeatures = [
      ...(lotes?.features || []),
      ...(imoveis?.features || []),
    ];

    if (allFeatures.length > 0) {
      const latLngs: L.LatLngExpression[] = [];

      allFeatures.forEach((feature) => {
        if (feature.geometry && feature.geometry.type === 'Point') {
          latLngs.push([feature.geometry.coordinates[1], feature.geometry.coordinates[0]]);
        } else if (feature.geometry && feature.geometry.type === 'Polygon') {
          feature.geometry.coordinates[0].forEach((coord: number[]) => {
            latLngs.push([coord[1], coord[0]]);
          });
        }
      });

      if (latLngs.length > 0) {
        setBounds(L.latLngBounds(latLngs));
      }
    }
  }, [lotes, imoveis]);

  // Estilo para lotes (preto)
  const lotesStyle = {
    color: '#000000',
    weight: 2,
    fillColor: '#000000',
    fillOpacity: 0.1,
  };

  // Estilo para imóveis (cinza escuro)
  const imoveisStyle = {
    color: '#333333',
    weight: 2,
    fillColor: '#666666',
    fillOpacity: 0.3,
  };

  // Estilo para círculo de análise
  const circleStyle = {
    color: '#000000',
    weight: 2,
    fillColor: '#ffffff',
    fillOpacity: 0.2,
    dashArray: '5, 5',
  };

  const onEachLote = (feature: any, layer: L.Layer) => {
    if (feature.properties) {
      const props = feature.properties;
      const popupContent = `
        <div style="color: #000; font-family: monospace; font-size: 12px;">
          <strong>Lote: ${props.codLote || 'N/A'}</strong><br/>
          <strong>Endereço:</strong> ${props.logradouro || ''} ${props.numero || ''}<br/>
          <strong>Bairro:</strong> ${props.bairro || 'N/A'}<br/>
          <strong>Área:</strong> ${props.area_terreno ? props.area_terreno.toFixed(2) + ' m²' : 'N/A'}<br/>
          ${props.ca ? `<strong>CA:</strong> ${props.ca}<br/>` : ''}
          ${props.to ? `<strong>TO:</strong> ${props.to}<br/>` : ''}
          ${props.altura ? `<strong>Altura:</strong> ${props.altura}m<br/>` : ''}
        </div>
      `;
      layer.bindPopup(popupContent);
    }
  };

  const onEachImovel = (feature: any, layer: L.Layer) => {
    if (feature.properties) {
      const props = feature.properties;
      const popupContent = `
        <div style="color: #000; font-family: monospace; font-size: 12px;">
          <strong>${props.empreendimento || 'Imóvel'}</strong><br/>
          <strong>Incorporador:</strong> ${props.incorporador || 'N/A'}<br/>
          <strong>Bairro:</strong> ${props.bairro || 'N/A'}<br/>
          <strong>Endereço:</strong> ${props.endereco || 'N/A'}<br/>
          ${props.dormitorios ? `<strong>Dormitórios:</strong> ${props.dormitorios}<br/>` : ''}
          ${props.metragem_privativa ? `<strong>Metragem:</strong> ${props.metragem_privativa}m²<br/>` : ''}
          ${props.preco_total ? `<strong>Preço:</strong> R$ ${props.preco_total.toLocaleString('pt-BR')}<br/>` : ''}
          ${props.status ? `<strong>Status:</strong> ${props.status}<br/>` : ''}
        </div>
      `;
      layer.bindPopup(popupContent);
    }
  };

  return (
    <MapContainer
      center={mapCenter}
      zoom={mapZoom}
      style={{ height: '100%', width: '100%', background: '#ffffff' }}
      zoomControl={true}
    >
      {/* TileLayer em preto e branco */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />

      {/* Lotes */}
      {lotes && lotes.features.length > 0 && (
        <GeoJSON
          key={`lotes-${lotes.features.length}`}
          data={lotes as any}
          style={lotesStyle}
          onEachFeature={onEachLote}
        />
      )}

      {/* Imóveis */}
      {imoveis && imoveis.features.length > 0 && (
        <GeoJSON
          key={`imoveis-${imoveis.features.length}`}
          data={imoveis as any}
          style={imoveisStyle}
          onEachFeature={onEachImovel}
        />
      )}

      {/* Círculo de análise */}
      {analysisResult && (
        <Circle
          center={[analysisResult.point.latitude, analysisResult.point.longitude]}
          radius={analysisResult.radius_meters}
          pathOptions={circleStyle}
        >
          <Popup>
            <div style={{ color: '#000', fontFamily: 'monospace', fontSize: '12px' }}>
              <strong>Análise Espacial</strong><br/>
              <strong>Raio:</strong> {analysisResult.radius_meters}m<br/>
              <strong>Lotes:</strong> {analysisResult.lotes_encontrados}<br/>
              <strong>Imóveis:</strong> {analysisResult.imoveis_encontrados}<br/>
            </div>
          </Popup>
        </Circle>
      )}

      {/* Handler de clique */}
      {onMapClick && <MapClickHandler onClick={onMapClick} />}

      {/* Ajustar bounds */}
      <FitBounds bounds={bounds} />
    </MapContainer>
  );
};

export default Map;
