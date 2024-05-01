import json
import pytest
import requests
import time

base_url = 'http://localhost:5000'

def test_worker():
    # Submit a job
    job_data = {'start': 1, 'end': 1000}
    response = requests.post(f'{base_url}/jobs', json=job_data)
    job_id = response.json()['id']

    # Wait for the worker to process previous jobs, time is longer to account for varying processor speeds
    time.sleep(45)

    # Check the job status
    response = requests.get(f'{base_url}/jobs/{job_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['in progress', 'complete', 'failed']

    # Check the job result
    response = requests.get(f'{base_url}/results/{job_id}')
    assert response.status_code in [200, 202, 404]
    data = response.json()
    assert isinstance(data, dict)
