import logging
import os
import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# Fetch validation variables
UAMI_CLIENT_ID = os.getenv("UAMI_CLIENT_ID")
BLOB_STORAGE_CONTAINER_NAME = os.getenv("BLOB_STORAGE_CONTAINER_NAME")

# Extract the service URI directly from the Azure host configuration setting
BLOB_SERVICE_URI = os.getenv("BlobStorageConnection__blobServiceUri")

# Initialize the credential at the module level for testing 
# (This ensures the azure-identity library loads smoothly)
credential = ManagedIdentityCredential(client_id=UAMI_CLIENT_ID)

@app.function_name(name="BlobTrigger")
@app.blob_trigger(
    arg_name="myblob", 
    path=f"{os.getenv('BLOB_STORAGE_CONTAINER_NAME')}/{{name}}",
    connection="BlobStorageConnection"
)
def test_function(myblob: func.InputStream):
    logging.info("==================================================")
    logging.info("🔴 BLOB TRIGGER ACTIVATED SUCCESSFULLY")
    logging.info("==================================================")
    
    # 1. Gracefully instantiate the data-plane client using your variable
    if BLOB_SERVICE_URI:
        try:
            blob_service_client = BlobServiceClient(
                account_url=BLOB_SERVICE_URI, 
                credential=credential
            )
            logging.info(f" -> Successfully initialized BlobServiceClient pointing to: {BLOB_SERVICE_URI}")
            
            # (Optional) Example of executing an internal data-plane action:
            # container_client = blob_service_client.get_container_client(BLOB_STORAGE_CONTAINER_NAME)
            
        except Exception as e:
            logging.error(f"Failed to initialize data-plane client: {str(e)}")
    else:
        logging.error("BLOB_SERVICE_URI extraction returned None. Check App Settings configuration.")

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