import json
import pytest
import requests

base_url = 'http://localhost:5000'

def test_load_data():
    response = requests.post(f'{base_url}/data')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert data['message'] == 'Data loaded into Redis'

def test_get_data():
    response = requests.get(f'{base_url}/data')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_delete_data():
    response = requests.delete(f'{base_url}/data')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert data['message'] == 'Data deleted from Redis'
    
    # Load the data back for other tests
    requests.post(f'{base_url}/data')

def test_get_gene_ids():
    response = requests.get(f'{base_url}/genes')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_gene_data():
    response = requests.get(f'{base_url}/genes')
    gene_ids = response.json()
    if gene_ids:
        gene_id = gene_ids[0]
        response = requests.get(f'{base_url}/genes/{gene_id}')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert 'hgnc_id' in data
    else:
        pytest.skip("No gene IDs available for testing")

def test_submit_job():
    job_data = {'start': 1, 'end': 10}
    response = requests.post(f'{base_url}/jobs', json=job_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'id' in data
    assert data['status'] == 'submitted'

def test_get_job_ids():
    response = requests.get(f'{base_url}/jobs')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_job():
    job_data = {'start': 1, 'end': 10}
    response = requests.post(f'{base_url}/jobs', json=job_data)
    job_id = response.json()['id']

    response = requests.get(f'{base_url}/jobs/{job_id}')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data['id'] == job_id

def test_get_result():
    job_data = {'start': 1, 'end': 10}
    response = requests.post(f'{base_url}/jobs', json=job_data)
    job_id = response.json()['id']

    response = requests.get(f'{base_url}/results/{job_id}')
    assert response.status_code in [200, 202, 404]
    data = response.json()
    assert isinstance(data, dict)
    assert 'status' in data
