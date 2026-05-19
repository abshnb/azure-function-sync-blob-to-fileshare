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
UAMI_CLIENT_ID = os.getenv("UAMI_CLIENT_ID")

if not BLOB_STORAGE_ACCOUNT_URL:
    raise ValueError("Missing required environment variable: BLOB_STORAGE_ACCOUNT_URL")
if not BLOB_STORAGE_CONTAINER_NAME:
    raise ValueError("Missing required environment variable: BLOB_STORAGE_CONTAINER_NAME")
if not BLOB_STORAGE_FILE_SHARE_MOUNT_PATH:
    raise ValueError("Missing required environment variable: BLOB_STORAGE_FILE_SHARE_MOUNT_PATH")
if not BLOB_TRIGGER_CONNECTION:
    raise ValueError("Missing required environment variable: BLOB_TRIGGER_CONNECTION")
if not UAMI_CLIENT_ID:
    raise ValueError("Missing required environment variable: UAMI_CLIENT_ID")

credential = ManagedIdentityCredential(client_id=UAMI_CLIENT_ID)

@app.blob_trigger(
    arg_name="myblob",
    path=BLOB_STORAGE_CONTAINER_NAME,
    connection=BLOB_TRIGGER_CONNECTION,
)
def funstorpocomar(myblob: func.InputStream):
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
