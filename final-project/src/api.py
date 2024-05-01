# !/usr/bin/env python3
from flask import Flask, jsonify, request
import requests
import redis
import logging
import json
from jobs import add_job, get_job_by_id, jdb, rd, rdb
import os

# Initialize Flask app and redis client
app = Flask(__name__)

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'WARNING')
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
URL = "https://g-a8b222.dd271.03c0.data.globus.org/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"

def fetch_hgnc_data() -> list:
    """
    Fetch HGNC gene data from the specified URL.

    Returns:
        list: A list of dictionaries representing the HGNC gene data. Each dictionary
              contains information about a gene.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        logging.info("Successfully fetched HGNC data")
        return data['response']['docs']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching HGNC data: {e}")
        raise

@app.route('/data', methods=['POST'])
def load_data() -> tuple:
    """
    Load HGNC data into Redis.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        data = fetch_hgnc_data()
        for gene in data:
            gene_json = json.dumps(gene)
            rd.set(gene['hgnc_id'], gene_json)
        logging.info("Data loaded into Redis")
        return jsonify({"status": "success", "message": "Data loaded into Redis"}), 200
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data', methods=['GET'])
def get_data() -> tuple:
    """
    Retrieve HGNC data from Redis.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        keys = rd.keys('*')
        data = []
        for key in keys:
            gene_json = rd.get(key)
            gene_data = json.loads(gene_json)
            data.append(gene_data)
        logging.info("Data retrieved from Redis")
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error retrieving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data', methods=['DELETE'])
def delete_data() -> tuple:
    """
    Delete HGNC data from Redis.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        rd.flushdb()
        logging.info("Data deleted from Redis")
        return jsonify({"status": "success", "message": "Data deleted from Redis"}), 200
    except Exception as e:
        logging.error(f"Error deleting data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/genes', methods=['GET'])
def get_gene_ids() -> tuple:
    """
    Retrieve HGNC gene IDs from Redis.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        keys = rd.keys()
        gene_ids = [key.decode('utf-8') for key in keys]
        logging.info("Gene IDs retrieved from redis")
        return jsonify(gene_ids), 200
    except Exception as e:
        logging.error(f"Error retrieving gene IDs: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/genes/<hgnc_id>', methods=['GET'])
def get_gene_data(hgnc_id: str) -> tuple:
    """
    Retrieve gene data for a specific HGNC ID from Redis.

    Args:
        hgnc_id (str): The HGNC ID of the gene.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        gene_json = rd.get(hgnc_id)
        if gene_json:
            gene_data = json.loads(gene_json)
            formatted_data = {
                "hgnc_id": gene_data.get("hgnc_id", ""),
                "symbol": gene_data.get("symbol", ""),
                "name": gene_data.get("name", ""),
                "locus_group": gene_data.get("locus_group", ""),
                "locus_type": gene_data.get("locus_type", ""),
                "status": gene_data.get("status", ""),
                "location": gene_data.get("location", ""),
                "location_sortable": gene_data.get("location_sortable", ""),
                "alias_symbol": gene_data.get("alias_symbol", [""])[0],
                "alias_name": gene_data.get("alias_name", [""])[0],
                "prev_symbol": gene_data.get("prev_symbol", [""])[0],
                "prev_name": gene_data.get("prev_name", [""])[0],
                "gene_group": gene_data.get("gene_group", [""])[0],
                "gene_group_id": gene_data.get("gene_group_id", [""])[0],
                "date_approved_reserved": gene_data.get("date_approved_reserved", ""),
                "date_symbol_changed": gene_data.get("date_symbol_changed", ""),
                "date_name_changed": gene_data.get("date_name_changed", ""),
                "date_modified": gene_data.get("date_modified", ""),
                "entrez_id": gene_data.get("entrez_id", ""),
                "ensembl_gene_id": gene_data.get("ensembl_gene_id", ""),
                "vega_id": gene_data.get("vega_id", ""),
                "ucsc_id": gene_data.get("ucsc_id", ""),
                "ena": gene_data.get("ena", ""),
                "refseq_accession": gene_data.get("refseq_accession", [""])[0],
                "ccds_id": gene_data.get("ccds_id", [""])[0],
                "uniprot_ids": gene_data.get("uniprot_ids", [""])[0],
                "pubmed_id": gene_data.get("pubmed_id", [""])[0],
                "mgd_id": gene_data.get("mgd_id", [""])[0],
                "rgd_id": gene_data.get("rgd_id", [""])[0],
                "lsdb": gene_data.get("lsdb", ""),
                "cosmic": gene_data.get("cosmic", ""),
                "omim_id": gene_data.get("omim_id", [""])[0],
                "mirbase": gene_data.get("mirbase", ""),
                "homeodb": gene_data.get("homeodb", ""),
                "snornabase": gene_data.get("snornabase", ""),
                "bioparadigms_slc": gene_data.get("bioparadigms_slc", ""),
                "orphanet": gene_data.get("orphanet", ""),
                "pseudogene.org": gene_data.get("pseudogene.org", ""),
                "horde_id": gene_data.get("horde_id", ""),
                "merops": gene_data.get("merops", ""),
                "imgt": gene_data.get("imgt", ""),
                "iuphar": gene_data.get("iuphar", ""),
                "kznf_gene_catalog": gene_data.get("kznf_gene_catalog", ""),
                "mamit-trnadb": gene_data.get("mamit-trnadb", ""),
                "cd": gene_data.get("cd", ""),
                "lncrnadb": gene_data.get("lncrnadb", ""),
                "enzyme_id": gene_data.get("enzyme_id", ""),
                "intermediate_filament_db": gene_data.get("intermediate_filament_db", ""),
                "rna_central_ids": gene_data.get("rna_central_ids", ""),
                "lncipedia": gene_data.get("lncipedia", ""),
                "gtrnadb": gene_data.get("gtrnadb", ""),
                "agr": gene_data.get("agr", ""),
                "mane_select": gene_data.get("mane_select", [""]),
                "gencc": gene_data.get("gencc", "")
            }
            logging.info(f"Gene data retrieved for HGNC ID: {hgnc_id}")
            return jsonify(formatted_data), 200
        else:
            logging.warning(f"Gene data not found for HGNC ID: {hgnc_id}")
            return jsonify({"status": "error", "message": "Gene not found"}), 404
    except Exception as e:
        logging.error(f"Error retrieving gene data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/jobs', methods=['POST'])
def submit_route() -> tuple:
    """
    Submit a job to the job queue.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    data = request.get_json()
    logging.debug(f"Received JSON data: {data}")
    job_dict = add_job(data['start'], data['end'])
    logging.debug(f"Job added: {job_dict}")
    return job_dict, 200

@app.route('/jobs', methods=['GET'])
def get_job_ids() -> tuple:
    """
    Retrieve job IDs from the job queue.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    job_ids = jdb.keys("*")
    job_ids = [job_id.decode('utf-8') for job_id in job_ids]
    logging.debug(f"Retrieved job IDs: {job_ids}")
    return jsonify(job_ids), 200

@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid: str) -> dict:
    """
    Retrieve a job by its ID.

    Args:
        jobid (str): The ID of the job.

    Returns:
        dict: The job dictionary.
    """
    return get_job_by_id(jobid)
        
@app.route('/results/<jobid>', methods=['GET'])
def get_result(jobid: str) -> tuple:
    """
    Retrieve the result of a job by its ID.

    Args:
        jobid (str): The ID of the job.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        job = get_job_by_id(jobid)
        if job:
            job_status = job['status']
            if job_status == 'complete':
                result_json = rdb.get(jobid)
                if result_json:
                    result = json.loads(result_json)
                    return jsonify({"status": "success", "result": result}), 200
                else:
                    return jsonify({"status": "error", "message": "Result not found"}), 404
            elif job_status == 'failed':
                return jsonify({"status": "error", "message": "Job failed"}), 500
            else:
                return jsonify({"status": "pending", "message": "Job is still in progress"}), 202
        else:
            return jsonify({"status": "error", "message": "Job not found"}), 404
    except Exception as e:
        logging.error(f"Error retrieving result for job {jobid}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/help', methods=['GET'])
def show_routes() -> tuple:
    """
    Display information about all the routes in the Flask application.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    routes = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            doc = app.view_functions[rule.endpoint].__doc__
            doc = ' '.join(doc.split()) if doc else ""
            routes[str(rule)] = {
                'methods': ','.join(rule.methods),
                'doc': doc,
            }
    return jsonify(routes), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
