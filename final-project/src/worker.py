from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
import os

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'WARNING')
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

@q.worker
def do_work(jobid: str) -> None:
    """
    Count the number of genes in each locus group based on parameters from a given job ID.

    Args:
        jobid (str): The ID of the job.
    """
    try:
        job = get_job_by_id(jobid)
        start = job['start']
        end = job['end']

        logging.info(f"Processing job {jobid}")
        update_job_status(jobid, "in progress")

        # Retrieve gene data from Redis within the specified range
        gene_data = []
        for gene_id in rd.keys():
            gene_json = rd.get(gene_id)
            gene = json.loads(gene_json)

            if start <= int(gene['hgnc_id'].split(':')[1]) <= end:
                gene_data.append(gene)

        # Count the number of genes in each locus group
        locus_group_counts = {}
        for gene in gene_data:
            locus_group = gene['locus_group']
            if locus_group in locus_group_counts:
                locus_group_counts[locus_group] += 1
            else:
                locus_group_counts[locus_group] = 1

        # Store the analysis result in the results database
        rdb.set(jobid, json.dumps(locus_group_counts))

        logging.info(f"Job {jobid} completed")
        update_job_status(jobid, "complete")
        
    except Exception as e:
        logging.error(f"Error processing job {jobid}: {e}")
        update_job_status(jobid, "failed")

do_work()
