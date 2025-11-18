import React, { useState, useEffect } from 'react';
import Map from './Map';
import {
  uploadLotes,
  uploadImoveis,
  getLotesGeoJSON,
  getImoveisGeoJSON,
  analyzeArea,
  getStats,
  GeoJSONCollection,
  AnalysisResponse,
  Stats,
} from './api';
import './App.css';

const App: React.FC = () => {
  const [lotes, setLotes] = useState<GeoJSONCollection | null>(null);
  const [imoveis, setImoveis] = useState<GeoJSONCollection | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [activePanel, setActivePanel] = useState<'upload' | 'analysis' | 'stats'>('upload');
  const [radiusMeters, setRadiusMeters] = useState(1000);
  const [selectedPoint, setSelectedPoint] = useState<{ lat: number; lng: number } | null>(null);

  // Carregar estatísticas ao iniciar
  useEffect(() => {
    loadStats();
  }, []);

  const showMessage = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleUploadLotes = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];
    setLoading(true);

    try {
      const response = await uploadLotes(file);
      showMessage(`${response.message}: ${response.records_count} registros`, 'success');
      await loadLotesData();
      await loadStats();
    } catch (error: any) {
      showMessage(`Erro ao carregar lotes: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  const handleUploadImoveis = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];
    setLoading(true);

    try {
      const response = await uploadImoveis(file);
      showMessage(`${response.message}: ${response.records_count} registros`, 'success');
      await loadImoveisData();
      await loadStats();
    } catch (error: any) {
      showMessage(`Erro ao carregar imóveis: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  const loadLotesData = async () => {
    setLoading(true);
    try {
      const data = await getLotesGeoJSON(undefined, 1000);
      setLotes(data);
      showMessage('Lotes carregados no mapa', 'success');
    } catch (error: any) {
      showMessage(`Erro ao carregar lotes: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadImoveisData = async () => {
    setLoading(true);
    try {
      const data = await getImoveisGeoJSON(undefined, 1000);
      setImoveis(data);
      showMessage('Imóveis carregados no mapa', 'success');
    } catch (error: any) {
      showMessage(`Erro ao carregar imóveis: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleMapClick = (lat: number, lng: number) => {
    setSelectedPoint({ lat, lng });
    showMessage(`Ponto selecionado: ${lat.toFixed(6)}, ${lng.toFixed(6)}`, 'info');
  };

  const handleAnalyze = async () => {
    if (!selectedPoint) {
      showMessage('Clique no mapa para selecionar um ponto primeiro', 'error');
      return;
    }

    setLoading(true);

    try {
      const result = await analyzeArea({
        latitude: selectedPoint.lat,
        longitude: selectedPoint.lng,
        radius_meters: radiusMeters,
      });

      setAnalysisResult(result);
      showMessage(
        `Análise concluída: ${result.lotes_encontrados} lotes, ${result.imoveis_encontrados} imóveis`,
        'success'
      );
    } catch (error: any) {
      showMessage(`Erro na análise: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>Sistema de Geoestatística Imobiliária</h1>
        <p>Análise Espacial de Dados Imobiliários</p>
      </header>

      {/* Main Content */}
      <div className="main-content">
        {/* Sidebar */}
        <aside className="sidebar">
          {/* Tabs */}
          <div className="tabs">
            <button
              className={`tab ${activePanel === 'upload' ? 'active' : ''}`}
              onClick={() => setActivePanel('upload')}
            >
              Upload
            </button>
            <button
              className={`tab ${activePanel === 'analysis' ? 'active' : ''}`}
              onClick={() => setActivePanel('analysis')}
            >
              Análise
            </button>
            <button
              className={`tab ${activePanel === 'stats' ? 'active' : ''}`}
              onClick={() => setActivePanel('stats')}
            >
              Estatísticas
            </button>
          </div>

          {/* Content */}
          <div className="panel-content">
            {activePanel === 'upload' && (
              <div className="panel">
                <h2>Carregar Dados</h2>

                <div className="upload-section">
                  <h3>Lotes de Vitória</h3>
                  <label className="file-input-label">
                    <input
                      type="file"
                      accept=".parquet"
                      onChange={handleUploadLotes}
                      disabled={loading}
                    />
                    <span>Selecionar arquivo .parquet</span>
                  </label>
                  {stats && stats.lotes.total > 0 && (
                    <button onClick={loadLotesData} disabled={loading} className="btn-secondary">
                      Visualizar Lotes
                    </button>
                  )}
                </div>

                <div className="upload-section">
                  <h3>Imóveis</h3>
                  <label className="file-input-label">
                    <input
                      type="file"
                      accept=".parquet"
                      onChange={handleUploadImoveis}
                      disabled={loading}
                    />
                    <span>Selecionar arquivo .parquet</span>
                  </label>
                  {stats && stats.imoveis.total > 0 && (
                    <button onClick={loadImoveisData} disabled={loading} className="btn-secondary">
                      Visualizar Imóveis
                    </button>
                  )}
                </div>
              </div>
            )}

            {activePanel === 'analysis' && (
              <div className="panel">
                <h2>Análise Espacial</h2>

                <div className="analysis-section">
                  <p className="instruction">Clique no mapa para selecionar um ponto</p>

                  {selectedPoint && (
                    <div className="selected-point">
                      <strong>Ponto Selecionado:</strong>
                      <div>Lat: {selectedPoint.lat.toFixed(6)}</div>
                      <div>Lng: {selectedPoint.lng.toFixed(6)}</div>
                    </div>
                  )}

                  <div className="input-group">
                    <label>Raio de Análise (metros)</label>
                    <input
                      type="number"
                      value={radiusMeters}
                      onChange={(e) => setRadiusMeters(Number(e.target.value))}
                      min="100"
                      max="5000"
                      step="100"
                    />
                  </div>

                  <button
                    onClick={handleAnalyze}
                    disabled={loading || !selectedPoint}
                    className="btn-primary"
                  >
                    Analisar Área
                  </button>

                  {analysisResult && (
                    <div className="analysis-results">
                      <h3>Resultados</h3>
                      <div className="result-item">
                        <span>Lotes encontrados:</span>
                        <strong>{analysisResult.lotes_encontrados}</strong>
                      </div>
                      <div className="result-item">
                        <span>Imóveis encontrados:</span>
                        <strong>{analysisResult.imoveis_encontrados}</strong>
                      </div>

                      {analysisResult.estatisticas.lotes.area_media && (
                        <div className="result-item">
                          <span>Área média dos lotes:</span>
                          <strong>{analysisResult.estatisticas.lotes.area_media.toFixed(2)} m²</strong>
                        </div>
                      )}

                      {analysisResult.estatisticas.imoveis.preco_medio && (
                        <div className="result-item">
                          <span>Preço médio:</span>
                          <strong>
                            R$ {analysisResult.estatisticas.imoveis.preco_medio.toLocaleString('pt-BR')}
                          </strong>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {activePanel === 'stats' && (
              <div className="panel">
                <h2>Estatísticas Gerais</h2>

                {stats && (
                  <div className="stats-section">
                    <div className="stat-group">
                      <h3>Lotes</h3>
                      <div className="stat-item">
                        <span>Total:</span>
                        <strong>{stats.lotes.total}</strong>
                      </div>
                      <div className="stat-item">
                        <span>Com geometria:</span>
                        <strong>{stats.lotes.com_geometria}</strong>
                      </div>
                      {stats.lotes.bairros_unicos !== undefined && (
                        <div className="stat-item">
                          <span>Bairros únicos:</span>
                          <strong>{stats.lotes.bairros_unicos}</strong>
                        </div>
                      )}
                    </div>

                    <div className="stat-group">
                      <h3>Imóveis</h3>
                      <div className="stat-item">
                        <span>Total:</span>
                        <strong>{stats.imoveis.total}</strong>
                      </div>
                      <div className="stat-item">
                        <span>Com geometria:</span>
                        <strong>{stats.imoveis.com_geometria}</strong>
                      </div>
                      {stats.imoveis.bairros_unicos !== undefined && (
                        <div className="stat-item">
                          <span>Bairros únicos:</span>
                          <strong>{stats.imoveis.bairros_unicos}</strong>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </aside>

        {/* Map */}
        <main className="map-container">
          <Map
            lotes={lotes}
            imoveis={imoveis}
            analysisResult={analysisResult}
            onMapClick={handleMapClick}
          />
        </main>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}

      {/* Message Toast */}
      {message && (
        <div className={`message-toast ${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default App;
