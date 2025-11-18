import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalysisRequest {
  latitude: number;
  longitude: number;
  radius_meters: number;
  filters?: Record<string, any>;
}

export interface AnalysisResponse {
  point: { latitude: number; longitude: number };
  radius_meters: number;
  lotes_encontrados: number;
  imoveis_encontrados: number;
  estatisticas: {
    lotes: Record<string, any>;
    imoveis: Record<string, any>;
  };
  lotes: GeoJSONFeature[];
  imoveis: GeoJSONFeature[];
}

export interface GeoJSONFeature {
  type: 'Feature';
  properties: Record<string, any>;
  geometry: any;
}

export interface GeoJSONCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export interface UploadResponse {
  message: string;
  records_count: number;
  file_type: string;
  columns: string[];
}

export interface Stats {
  lotes: {
    total: number;
    com_geometria: number;
    bairros_unicos?: number;
  };
  imoveis: {
    total: number;
    com_geometria: number;
    bairros_unicos?: number;
  };
}

export interface Bounds {
  bounds: {
    minLng: number;
    minLat: number;
    maxLng: number;
    maxLat: number;
  } | null;
  message?: string;
}

// API Calls
export const uploadLotes = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/lotes', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const uploadImoveis = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/imoveis', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const analyzeArea = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post('/analyze', request);
  return response.data;
};

export const getLotesGeoJSON = async (bairro?: string, limit?: number): Promise<GeoJSONCollection> => {
  const params = new URLSearchParams();
  if (bairro) params.append('bairro', bairro);
  if (limit) params.append('limit', limit.toString());

  const response = await api.get(`/lotes/geojson?${params.toString()}`);
  return response.data;
};

export const getImoveisGeoJSON = async (bairro?: string, limit?: number): Promise<GeoJSONCollection> => {
  const params = new URLSearchParams();
  if (bairro) params.append('bairro', bairro);
  if (limit) params.append('limit', limit.toString());

  const response = await api.get(`/imoveis/geojson?${params.toString()}`);
  return response.data;
};

export const getBounds = async (): Promise<Bounds> => {
  const response = await api.get('/bounds');
  return response.data;
};

export const getStats = async (): Promise<Stats> => {
  const response = await api.get('/stats');
  return response.data;
};

export const healthCheck = async (): Promise<{ status: string; timestamp: string; version: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
