"""
Script de teste para a API Flask
Exemplos de como usar todos os endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Testa o endpoint de health check"""
    print("\n=== Testando Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_upload_lotes(file_path):
    """Testa o upload de arquivo de lotes"""
    print("\n=== Testando Upload de Lotes ===")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/octet-stream')}
            response = requests.post(f"{BASE_URL}/upload/lotes", files=files)
            print(f"Status: {response.status_code}")
            print(f"Resposta: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return False


def test_upload_imoveis(file_path):
    """Testa o upload de arquivo de imóveis"""
    print("\n=== Testando Upload de Imóveis ===")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/octet-stream')}
            response = requests.post(f"{BASE_URL}/upload/imoveis", files=files)
            print(f"Status: {response.status_code}")
            print(f"Resposta: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return False


def test_stats():
    """Testa o endpoint de estatísticas"""
    print("\n=== Testando Estatísticas ===")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_bounds():
    """Testa o endpoint de bounds"""
    print("\n=== Testando Bounds ===")
    response = requests.get(f"{BASE_URL}/bounds")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_lotes_geojson(bairro=None, limit=10):
    """Testa o endpoint de lotes GeoJSON"""
    print("\n=== Testando Lotes GeoJSON ===")
    params = {}
    if bairro:
        params['bairro'] = bairro
    if limit:
        params['limit'] = limit

    response = requests.get(f"{BASE_URL}/lotes/geojson", params=params)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Número de features: {len(data.get('features', []))}")
    if data.get('features'):
        print(f"Primeira feature: {json.dumps(data['features'][0], indent=2)[:300]}...")
    return response.status_code == 200


def test_imoveis_geojson(bairro=None, limit=10):
    """Testa o endpoint de imóveis GeoJSON"""
    print("\n=== Testando Imóveis GeoJSON ===")
    params = {}
    if bairro:
        params['bairro'] = bairro
    if limit:
        params['limit'] = limit

    response = requests.get(f"{BASE_URL}/imoveis/geojson", params=params)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Número de features: {len(data.get('features', []))}")
    if data.get('features'):
        print(f"Primeira feature: {json.dumps(data['features'][0], indent=2)[:300]}...")
    return response.status_code == 200


def test_analyze(latitude=-20.3155, longitude=-40.3128, radius_meters=1000):
    """Testa o endpoint de análise espacial"""
    print("\n=== Testando Análise Espacial ===")
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "radius_meters": radius_meters,
        "filters": {}
    }
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("INICIANDO TESTES DA API FLASK")
    print("=" * 60)

    results = []

    # Teste básico
    results.append(("Health Check", test_health()))

    # Testes que não dependem de dados
    results.append(("Stats (sem dados)", test_stats()))
    results.append(("Bounds (sem dados)", test_bounds()))
    results.append(("Lotes GeoJSON (sem dados)", test_lotes_geojson()))
    results.append(("Imóveis GeoJSON (sem dados)", test_imoveis_geojson()))

    # Teste de análise espacial (sem dados)
    results.append(("Análise Espacial (sem dados)", test_analyze()))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} testes passaram")


if __name__ == "__main__":
    import sys

    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ Servidor Flask está rodando em {BASE_URL}")
        else:
            print(f"⚠️  Servidor respondeu com status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro: Não foi possível conectar ao servidor em {BASE_URL}")
        print("Certifique-se de que o servidor Flask está rodando:")
        print("  python app.py")
        print("  ou")
        print("  flask run --host=0.0.0.0 --port=8000")
        sys.exit(1)

    # Executar todos os testes
    run_all_tests()

    print("\n" + "=" * 60)
    print("Para testar upload de arquivos, execute:")
    print("  python test_api.py upload /path/to/lotes.parquet")
    print("  python test_api.py upload /path/to/imoveis.parquet")
    print("=" * 60)
