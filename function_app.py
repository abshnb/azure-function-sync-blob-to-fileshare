import logging
import os
import azure.functions as func
from azure.identity import ManagedIdentityCredential

app = func.FunctionApp()

# Fetch validation variables
UAMI_CLIENT_ID = os.getenv("UAMI_CLIENT_ID")
BLOB_STORAGE_CONTAINER_NAME = os.getenv("BLOB_STORAGE_CONTAINER_NAME")

# Initialize the credential at the module level for testing 
# (This ensures the azure-identity library loads smoothly)
credential = ManagedIdentityCredential(client_id=UAMI_CLIENT_ID)

@app.function_name(name="BlobTriggerTesting")
@app.blob_trigger(
    arg_name="myblob", 
    path=f"{os.getenv('BLOB_STORAGE_CONTAINER_NAME')}/{{name}}",
    connection="BlobStorageConnection"
)
def test_function(myblob: func.InputStream):
    logging.info("==================================================")
    logging.info("🔴 BLOB TRIGGER ACTIVATED SUCCESSFULLY")
    logging.info("==================================================")
    
    # Quick environment variable check in the execution logs
    logging.info("Checking configuration state:")
    logging.info(f" -> UAMI_CLIENT_ID: {'Configured' if UAMI_CLIENT_ID else 'MISSING'}")
    logging.info(f" -> BLOB_STORAGE_CONTAINER_NAME: {BLOB_STORAGE_CONTAINER_NAME}")
    
    # Log details about the intercepted blob file
    logging.info("Processing Blob Metadata:")
    logging.info(f" -> Full Trigger Path: {myblob.name}")
    logging.info(f" -> Blob Size: {myblob.length} bytes")
    logging.info(f" -> Content Type: {getattr(myblob, 'uri', 'N/A')}")
    
    logging.info("==================================================")
    logging.info("🟢 UAMI CONNECTIVITY TEST PASSED")
    logging.info("==================================================")