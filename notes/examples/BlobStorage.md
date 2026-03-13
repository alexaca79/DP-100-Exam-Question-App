# What is Azure Blob Storage?

Azure **Blob Storage** is a cloud object storage service from **Microsoft Azure** designed to store large amounts of unstructured data. It's ideal for storing files like images, videos, documents, log files, and backups.

Blob Storage is NOT a database — it's an object storage system (files), similar to AWS S3. 
---

## Key Features
- **Scalability:** Can handle from small files to petabytes of data with ease.
- **High Availability:** Automatic replication to ensure data is safe.
- **Accessible from anywhere:** Can be accessed via the REST API, Azure SDKs, PowerShell, and Azure CLI.
- **Cost Efficient:** Has hot and cool storage tiers based on access frequency.  

---

## Types of Blobs in Azure Storage

### 1. Block Blob
- Stores files like images, documents, videos, and backups.
- Ideal for files with **frequent access or little change**.

### 2. Append Blob
- Similar to Block Blob, but designed to **append data without modifying existing content**.
- Useful for **log files and audit trails**.

### 3. Page Blob
- Designed for **large files that need fast random access**.
- Used for virtual machine disks (Azure VHDs).  

---

## Common Use Cases
- Storage of images and videos for web applications
- Data lakes for big data and analytics
- Backup and disaster recovery
- IoT file storage and application logs

---

## Example: Create a Blob Storage with Python (Azure SDK)

````python
from azure.storage.blob import BlobServiceClient

# Connect to Blob Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create a container
container_name = "my-files"
container_client = blob_service_client.create_container(container_name)

# Upload a file
blob_client = container_client.get_blob_client("file.txt")
with open("file.txt", "rb") as data:
    blob_client.upload_blob(data)

print("File uploaded successfully.")

```