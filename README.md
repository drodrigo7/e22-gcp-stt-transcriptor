# Transcription CLI with GCP's Speech-to-Text
The following repository holds a Python CLI which aims to 
perform transcriptions of long audio files using Speech-to-Text V2 API 
from GCP. Read the following README.md file for configurations required.

## Google Cloud
### GCP SDK

This script requires to install and configure the CLI for Google Cloud in 
order to use Python client and interact with GCP services. Refer to installation documentation ([docs](https://cloud.google.com/sdk/docs/install)).

---

### GCP SDK Configuration
1. **CLI Initialization**  
If no other configuration is found for SDK, execute the following command:
```bash
gcloud init
```

2. **Default Credentials**  
User local credentials for Python client (no JSON keys):
```bash
gcloud auth application-default login
```

3. **Storage Bucket**  
This resource if required for long running transcriptions.
If no other bucket is available, the following command deploys a single bucket:
```bash
gcloud storage buckets create "gs://{bucket-name}" --project="{project-id}" --location="us-central1" 
```

4. **GCP Speech-to-Text API**  
This service needs to be enabled in the GCP project.
Refer to GCP console for enabling the service ([console](https://console.cloud.google.com/apis/api/speech.googleapis.com/overview)) or execute the following command:
```bash
gcloud services enable speech.googleapis.com
```

---

## GCP Pricing
1. **Speech-to-Text V2**  
This script uses Dynamic batch speech recognition from Speech to Text API V2
for the transcription ([docs](https://cloud.google.com/speech-to-text/v2/docs/batch-recognize)).
Pricing for this API is **0.003 USD per minute** ([docs](https://cloud.google.com/speech-to-text/pricing)).

2. **Google Cloud Storage**  
Pricing due to this service depends on size of stored data (USD/GB per month), bucket configurations and operations. Refer to pricing documentation ([docs](https://cloud.google.com/storage/pricing)).
By default, the suggested command from above deploys a bucket in a single region (`us-central1`)
and of type `Standard Storage`.

---

## Environment Configuration
### 1. Directories
```bash
mkdir -p ./assets/downloads ./assets/temp ./assets/tracking
```

### 2. Environment variables
The following commands will create a `.env` file that stores GCP project ID and
the GCS bucket name. Replace with corresponding values.
```bash
echo "GCP_PROJECT_ID=\"{project-id}\"" >> ./.env
echo "GCP_BUCKET_NAME=\"{bucket-name}\"" >> ./.env
```

### 3. Virtual environment
```bash
python -m venv env
env\Scripts\activate.bat
pip3 install -r requirements.txt
```

### 4. CLI usage
See available commands at:
```bash
python src/main.py --help
```

See help for individual commands:
```bash
python src/main.py {command} --help
```

---

## Additional resources
* Google transcription models: https://cloud.google.com/speech-to-text/v2/docs/transcription-model
* Chirp language model: https://cloud.google.com/speech-to-text/v2/docs/chirp-model
* Speech-to-Text pricing: https://cloud.google.com/speech-to-text/pricing
* GCP Operations Python client: https://googleapis.dev/python/google-api-core/latest/operation.html
* GCP Speech-to-Text Python client: https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v2.services.speech.SpeechClient
* GCP Speech-to-Text API recognizers: https://cloud.google.com/speech-to-text/v2/docs/reference/rest/v2/projects.locations.recognizers/batchRecognize
