# ¿Qué es un Blob Storage en Azure?

Azure **Blob Storage** es un servicio de almacenamiento de objetos en la nube de **Microsoft Azure** diseñado para almacenar grandes cantidades de datos no estructurados. Es ideal para almacenar archivos como imágenes, videos, documentos, archivos de registro y copias de seguridad.

Blob Storage NO es una base de datos, es un sistema de almacenamiento de objetos (Archivos), similar a AWS S3. 
---

## Características principales
✅ **Escalabilidad:** Puede manejar desde pequeños archivos hasta petabytes de datos sin problemas.  
✅ **Alta disponibilidad:** Replicación automática para garantizar que los datos estén seguros.  
✅ **Accesible desde cualquier lugar:** Se puede acceder mediante la API REST, SDKs de Azure, PowerShell y la CLI de Azure.  
✅ **Costo eficiente:** Tiene opciones de almacenamiento en frío y caliente según la frecuencia de acceso.  

---

## Tipos de blobs en Azure Storage

### 1. Block Blob 🧱
- Almacena archivos como imágenes, documentos, videos y backups.  
- Ideal para archivos de **acceso frecuente o poco cambio**.  

### 2. Append Blob 📜
- Similar a Block Blob, pero diseñado para **agregar datos sin modificar los existentes**.  
- Útil para **archivos de registro y auditorías**.  

### 3. Page Blob 📖
- Diseñado para **almacenar archivos grandes y que necesitan acceso rápido**.  
- Usado en discos virtuales de máquinas virtuales (VHDs de Azure).  

---

## Casos de uso comunes
- 🔹 **Almacenamiento de imágenes y videos para aplicaciones web**  
- 🔹 **Data lakes para big data y análisis**  
- 🔹 **Copia de seguridad y recuperación ante desastres**  
- 🔹 **Almacenamiento de archivos de IoT y logs de aplicaciones**  

---

## Ejemplo: Crear un Blob Storage con Python (SDK de Azure)

````python
from azure.storage.blob import BlobServiceClient

# Conexión al Blob Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=tu_cuenta;AccountKey=tu_clave"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Crear un contenedor
container_name = "mis-archivos"
container_client = blob_service_client.create_container(container_name)

# Subir un archivo
blob_client = container_client.get_blob_client("archivo.txt")
with open("archivo.txt", "rb") as data:
    blob_client.upload_blob(data)

print("Archivo subido exitosamente.")

```