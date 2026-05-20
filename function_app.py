import logging
import os
from pathlib import Path

import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient

app = func.FunctionApp()

BLOB_STORAGE_ACCOUNT_URL = os.getenv("BLOB_STORAGE_ACCOUNT_URL")
BLOB_STORAGE_CONTAINER_NAME = os.getenv("BLOB_STORAGE_CONTAINER_NAME")
BLOB_STORAGE_FILE_SHARE_MOUNT_PATH = os.getenv("BLOB_STORAGE_FILE_SHARE_MOUNT_PATH")
BLOB_TRIGGER_CONNECTION = os.getenv("BLOB_TRIGGER_CONNECTION")
"""
Configuration is read at import time but validation is deferred to the
trigger handler so import-time exceptions don't prevent function discovery.
The function uses the system-assigned managed identity (no client id).
"""

credential = ManagedIdentityCredential()

@app.blob_trigger(
    arg_name="myblob",
    path=BLOB_STORAGE_CONTAINER_NAME,
    connection=BLOB_TRIGGER_CONNECTION,
)
def funstorpocomar(myblob: func.InputStream):
    # perform runtime validation of required settings so the host can discover
    # functions even if configuration is incomplete; fail the invocation
    # gracefully with logs if required settings are missing.
    missing = []
    if not BLOB_STORAGE_ACCOUNT_URL:
        missing.append("BLOB_STORAGE_ACCOUNT_URL")
    if not BLOB_STORAGE_CONTAINER_NAME:
        missing.append("BLOB_STORAGE_CONTAINER_NAME")
    if not BLOB_STORAGE_FILE_SHARE_MOUNT_PATH:
        missing.append("BLOB_STORAGE_FILE_SHARE_MOUNT_PATH")
    if not BLOB_TRIGGER_CONNECTION:
        missing.append("BLOB_TRIGGER_CONNECTION")

    if missing:
        logging.error("Missing required environment variables: %s", ",".join(missing))
        return

    blob_name = myblob.name
    if blob_name.startswith(f"{BLOB_STORAGE_CONTAINER_NAME}/"):
        blob_name = blob_name[len(f"{BLOB_STORAGE_CONTAINER_NAME}/") :]

    logging.info(
        "Python blob trigger function processed blob. Name: %s. Size: %s bytes",
        blob_name,
        myblob.length,
    )

    blob_client = BlobClient(
        account_url=BLOB_STORAGE_ACCOUNT_URL,
        container_name=BLOB_STORAGE_CONTAINER_NAME,
        blob_name=blob_name,
        credential=credential,
    )

    destination_path = Path(BLOB_STORAGE_FILE_SHARE_MOUNT_PATH) / Path(blob_name)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    with blob_client.download_blob() as download_stream:
        with destination_path.open("wb") as dest_file:
            dest_file.write(download_stream.readall())

    logging.info("Downloaded blob %s to mount path %s", blob_name, destination_path)
