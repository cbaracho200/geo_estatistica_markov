// ========================================
// VARIÁVEIS GLOBAIS
// ========================================
let map;
let lotesLayer;
let imoveisLayer;
let analysisLayer;
let analysisCircle;
const API_BASE = window.location.origin;

// ========================================
// INICIALIZAÇÃO DO MAPA
// ========================================
function initMap() {
    // Criar mapa centrado em Vitória, ES
    map = L.map('map').setView([-20.3155, -40.3128], 13);

    // Adicionar tile layer (preto e branco)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19
    }).addTo(map);

    // Criar layers para lotes e imóveis
    lotesLayer = L.layerGroup().addTo(map);
    imoveisLayer = L.layerGroup().addTo(map);
    analysisLayer = L.layerGroup().addTo(map);

    // Adicionar evento de clique no mapa para análise
    map.on('click', onMapClick);

    console.log('Mapa inicializado');
}

// ========================================
// UPLOAD DE ARQUIVOS
// ========================================
async function uploadLotes() {
    const fileInput = document.getElementById('lotes-file');
    const statusDiv = document.getElementById('lotes-status');

    if (!fileInput.files.length) {
        statusDiv.textContent = 'Selecione um arquivo';
        statusDiv.className = 'status-message error';
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    statusDiv.textContent = 'Enviando arquivo...';
    statusDiv.className = 'status-message loading';

    try {
        const response = await fetch(`${API_BASE}/upload/lotes`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            statusDiv.textContent = `✓ ${data.message} (${data.records_count} registros)`;
            statusDiv.className = 'status-message success';
            loadStats();
            loadMapData();
        } else {
            statusDiv.textContent = `✗ Erro: ${data.detail}`;
            statusDiv.className = 'status-message error';
        }
    } catch (error) {
        statusDiv.textContent = `✗ Erro: ${error.message}`;
        statusDiv.className = 'status-message error';
    }
}

async function uploadImoveis() {
    const fileInput = document.getElementById('imoveis-file');
    const statusDiv = document.getElementById('imoveis-status');

    if (!fileInput.files.length) {
        statusDiv.textContent = 'Selecione um arquivo';
        statusDiv.className = 'status-message error';
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    statusDiv.textContent = 'Enviando arquivo...';
    statusDiv.className = 'status-message loading';

    try {
        const response = await fetch(`${API_BASE}/upload/imoveis`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            statusDiv.textContent = `✓ ${data.message} (${data.records_count} registros)`;
            statusDiv.className = 'status-message success';
            loadStats();
            loadMapData();
        } else {
            statusDiv.textContent = `✗ Erro: ${data.detail}`;
            statusDiv.className = 'status-message error';
        }
    } catch (error) {
        statusDiv.textContent = `✗ Erro: ${error.message}`;
        statusDiv.className = 'status-message error';
    }
}

// ========================================
// ESTATÍSTICAS
// ========================================
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        document.getElementById('lotes-total').textContent = data.lotes.total || 0;
        document.getElementById('lotes-geometria').textContent = data.lotes.com_geometria || 0;
        document.getElementById('imoveis-total').textContent = data.imoveis.total || 0;
        document.getElementById('imoveis-geometria').textContent = data.imoveis.com_geometria || 0;
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ========================================
// CARREGAR DADOS NO MAPA
// ========================================
async function loadMapData() {
    const bairro = document.getElementById('bairro-filter').value;
    const limit = document.getElementById('limit-filter').value;
    const showLotes = document.getElementById('show-lotes').checked;
    const showImoveis = document.getElementById('show-imoveis').checked;

    // Limpar layers
    lotesLayer.clearLayers();
    imoveisLayer.clearLayers();

    // Carregar lotes
    if (showLotes) {
        await loadLotes(bairro, limit);
    }

    // Carregar imóveis
    if (showImoveis) {
        await loadImoveis(bairro, limit);
    }

    // Ajustar bounds do mapa
    await adjustMapBounds();
}

async function loadLotes(bairro, limit) {
    try {
        let url = `${API_BASE}/lotes/geojson?limit=${limit}`;
        if (bairro) {
            url += `&bairro=${encodeURIComponent(bairro)}`;
        }

        const response = await fetch(url);
        const geojson = await response.json();

        if (geojson.features && geojson.features.length > 0) {
            L.geoJSON(geojson, {
                style: {
                    color: '#000000',
                    weight: 2,
                    fillColor: '#000000',
                    fillOpacity: 0.1
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties;
                    const popup = `
                        <div style="font-family: 'Courier New', monospace;">
                            <strong>LOTE</strong><br>
                            Código: ${props.codLote || '-'}<br>
                            Bairro: ${props.bairro || '-'}<br>
                            Área: ${props.area_terreno ? props.area_terreno.toFixed(2) + ' m²' : '-'}<br>
                            Logradouro: ${props.logradouro || '-'}<br>
                            Número: ${props.numero || '-'}
                        </div>
                    `;
                    layer.bindPopup(popup);
                }
            }).addTo(lotesLayer);

            console.log(`${geojson.features.length} lotes carregados`);
        }
    } catch (error) {
        console.error('Erro ao carregar lotes:', error);
    }
}

async function loadImoveis(bairro, limit) {
    try {
        let url = `${API_BASE}/imoveis/geojson?limit=${limit}`;
        if (bairro) {
            url += `&bairro=${encodeURIComponent(bairro)}`;
        }

        const response = await fetch(url);
        const geojson = await response.json();

        if (geojson.features && geojson.features.length > 0) {
            L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, {
                        radius: 6,
                        fillColor: '#666666',
                        color: '#000000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    });
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties;
                    const popup = `
                        <div style="font-family: 'Courier New', monospace;">
                            <strong>IMÓVEL</strong><br>
                            Empreendimento: ${props.empreendimento || props.Empreendimento || '-'}<br>
                            Bairro: ${props.bairro || props.Bairro || '-'}<br>
                            Dormitórios: ${props.dormitorios || props.Dormitorios || '-'}<br>
                            Metragem: ${props.metragem_privativa || props['Metragem Privativa'] ? (props.metragem_privativa || props['Metragem Privativa']).toFixed(2) + ' m²' : '-'}<br>
                            Preço: ${props.preco_total || props['Preco Total'] ? 'R$ ' + (props.preco_total || props['Preco Total']).toLocaleString('pt-BR') : '-'}
                        </div>
                    `;
                    layer.bindPopup(popup);
                }
            }).addTo(imoveisLayer);

            console.log(`${geojson.features.length} imóveis carregados`);
        }
    } catch (error) {
        console.error('Erro ao carregar imóveis:', error);
    }
}

async function adjustMapBounds() {
    try {
        const response = await fetch(`${API_BASE}/bounds`);
        const data = await response.json();

        if (data.bounds) {
            const bounds = [
                [data.bounds.minLat, data.bounds.minLng],
                [data.bounds.maxLat, data.bounds.maxLng]
            ];
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    } catch (error) {
        console.error('Erro ao ajustar bounds:', error);
    }
}

// ========================================
// CONTROLES DE VISUALIZAÇÃO
// ========================================
function toggleLotes() {
    const showLotes = document.getElementById('show-lotes').checked;
    if (showLotes) {
        map.addLayer(lotesLayer);
    } else {
        map.removeLayer(lotesLayer);
    }
}

function toggleImoveis() {
    const showImoveis = document.getElementById('show-imoveis').checked;
    if (showImoveis) {
        map.addLayer(imoveisLayer);
    } else {
        map.removeLayer(imoveisLayer);
    }
}

// ========================================
// ANÁLISE ESPACIAL
// ========================================
async function onMapClick(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;
    const radius = parseInt(document.getElementById('radius-input').value);

    // Limpar análise anterior
    analysisLayer.clearLayers();

    // Adicionar círculo no mapa
    analysisCircle = L.circle([lat, lng], {
        radius: radius,
        color: '#000000',
        fillColor: '#000000',
        fillOpacity: 0.1,
        weight: 2,
        dashArray: '5, 5'
    }).addTo(analysisLayer);

    // Adicionar marcador no centro
    L.marker([lat, lng], {
        icon: L.divIcon({
            className: 'analysis-marker',
            html: '<div style="background: #000; width: 10px; height: 10px; border: 2px solid #fff; border-radius: 50%;"></div>',
            iconSize: [10, 10]
        })
    }).addTo(analysisLayer);

    // Fazer análise
    await analyzeArea(lat, lng, radius);
}

async function analyzeArea(lat, lng, radius) {
    const resultDiv = document.getElementById('analysis-result');
    resultDiv.innerHTML = '<div class="loading">Analisando área</div>';

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: lat,
                longitude: lng,
                radius_meters: radius
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayAnalysisResult(data);
        } else {
            resultDiv.innerHTML = `<div class="error">Erro: ${data.detail}</div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

function displayAnalysisResult(data) {
    const resultDiv = document.getElementById('analysis-result');

    let html = '<div style="font-size: 12px;">';
    html += `<strong>PONTO ANALISADO</strong><br>`;
    html += `Lat: ${data.point.latitude.toFixed(6)}<br>`;
    html += `Lng: ${data.point.longitude.toFixed(6)}<br>`;
    html += `Raio: ${data.radius_meters}m<br><br>`;

    html += `<strong>RESULTADOS</strong><br>`;
    html += `Lotes encontrados: ${data.lotes_encontrados}<br>`;
    html += `Imóveis encontrados: ${data.imoveis_encontrados}<br><br>`;

    if (data.estatisticas.lotes && Object.keys(data.estatisticas.lotes).length > 0) {
        html += `<strong>ESTATÍSTICAS DE LOTES</strong><br>`;
        if (data.estatisticas.lotes.area_media) {
            html += `Área média: ${data.estatisticas.lotes.area_media.toFixed(2)} m²<br>`;
        }
        if (data.estatisticas.lotes.area_total) {
            html += `Área total: ${data.estatisticas.lotes.area_total.toFixed(2)} m²<br>`;
        }
        html += '<br>';
    }

    if (data.estatisticas.imoveis && Object.keys(data.estatisticas.imoveis).length > 0) {
        html += `<strong>ESTATÍSTICAS DE IMÓVEIS</strong><br>`;
        if (data.estatisticas.imoveis.preco_medio) {
            html += `Preço médio: R$ ${data.estatisticas.imoveis.preco_medio.toLocaleString('pt-BR')}<br>`;
        }
        if (data.estatisticas.imoveis.metragem_media) {
            html += `Metragem média: ${data.estatisticas.imoveis.metragem_media.toFixed(2)} m²<br>`;
        }
    }

    html += '</div>';

    resultDiv.innerHTML = html;
}

// ========================================
// INICIALIZAÇÃO
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Iniciando aplicação...');
    initMap();
    loadStats();
    console.log('Aplicação pronta!');
});
