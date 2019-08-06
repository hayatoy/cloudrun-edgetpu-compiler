import os
import subprocess
import tempfile
import re
from flask import Flask, request
from google.cloud import storage

app = Flask(__name__)


def download_blob(gcs_uri, destination_file_name):
    """Downloads a blob from the bucket."""
    bucket_name = os.path.split(gcs_uri.strip())[0].replace("gs://", "")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_uri.replace("gs://" + bucket_name + "/", ""))
    with open(destination_file_name, "wb") as f:
        client.download_blob_to_file(blob, f)


def upload_blob(gcs_uri, source_file_name):
    """Uploads a file to the bucket."""
    bucket_name = os.path.split(gcs_uri)[0].replace("gs://", "")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_uri.replace("gs://" + bucket_name + "/", ""))
    blob.upload_from_filename(source_file_name)


@app.route('/compile', methods=['POST'])
def compile():
    with tempfile.TemporaryDirectory() as tdir:
        gcs_src_uri = request.form['gcs_src_uri']
        gcs_dst_uri = request.form['gcs_dst_uri']
        
        src_file_paths = []
        for gcs_uri in gcs_src_uri.split(","):
            filename = os.path.basename(gcs_uri)
            src_file_path = os.path.join(tdir, filename)
            download_blob(gcs_uri, src_file_path)
            src_file_paths.append(src_file_path)

        cmd_list = ["edgetpu_compiler"] + src_file_paths + ["-o", tdir]
        proc = subprocess.run(cmd_list,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = proc.stdout.decode("utf8")

        m = re.search(r"Output model: .*", ret)
        if m:
            dst_file_path = m.group(0).replace("Output model: ", "")
            upload_blob(gcs_dst_uri, dst_file_path)

        return ret


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
