# ./main.py
# ==================================================
# settings
import dotenv; dotenv.load_dotenv()
# --------------------------------------------------
# standard
from datetime import datetime
from typing import Optional
# requirements
import typer
from typer import Option
# defined
from modules.service import Service
# --------------------------------------------------

app = typer.Typer()

@app.command(hidden=1)
def __hidden() -> None:
    return

@app.command()
def vta(
    video_path: str = Option(help='Local video path (ex: /path/to/video.mp4).')
) -> None:
    '''(v)ideo (t)o (a)udio
    
    Extracts the audio from a video and saves it in a local directory as a WAV file.
    '''
    saving_path = './assets/temp/'
    Service.retrieve_audio(video_path, saving_path)
    return

@app.command()
def ftc(
    bucket_name: str = Option(help='GCP bucket name', envvar='GCP_BUCKET_NAME'),
    src_file: str = Option(help='Source file to be uploaded.'),
    blob_name: str = Option(help='Blob name in Cloud Storage.')
) -> None:
    '''(f)ile (t)o (c)loud
    
    Uploads a local file to a bucket in Google Cloud Storage.
    '''
    Service.file_to_gcs(bucket_name, src_file, blob_name.strip('/'))
    return

@app.command()
def att(
    project_id: str = Option(help='GCP project ID', envvar='GCP_PROJECT_ID'),
    bucket_name: str = Option(help='GCS bucket', envvar='GCP_BUCKET_NAME'),
    language_code: str = Option(help='Language code for Chirp language model', envvar='GCP_LANGUAGE_CODE'),
    src_blob: str = Option(help='Source blob of audio file.'),
    dst_blob: str = Option(help='Destination blob for Speech-to-Text output.'),
) -> None:
    '''(a)udio (t)o (t)ext
    
    This command makes a request to the Speech-to-Text V2 API for a dynamic batch
    long running operation.
    '''
    src_uri = f'gs://{bucket_name}/{src_blob.strip('/')}'
    dst_uri = f'gs://{bucket_name}/{dst_blob.strip('/')}'
    tracking_file = './assets/tracking/requests/{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    Service.dynamic_batch_transcription(project_id, src_uri, dst_uri, tracking_file, language_code)
    return

@app.command()
def rto(
    operation_name: str = Option(help='Name of long running operation from GCP Speech-to-Text V2 API.')
) -> None:
    '''(r)etrieve (t)ranscript (o)peration
    
    This command checks the status of a GCP long running operation for a request to
    Speech-to-Text V2 API.
    `operation_name` format: projects/{project-id}/locations/{region}/operations/{operation}
    '''
    tracking_file = './assets/tracking/validation/{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    Service.retrieve_transcript(operation_name, tracking_file)
    return

@app.command()
def ctl(
    bucket_name: str = Option(help='GCS bucket', envvar='GCP_BUCKET_NAME'),
    src_blob: str = Option(help='GCS path for blob/folder.'),
    folder: Optional[bool] = Option(False, help='Flag that indicates if `src_blob` is a GCS folder.')
) -> None:
    '''(c)loud (t)o (l)ocal
    
    Downloads a blob or folder from Google Cloud Storage bucket into a local directory.
    '''
    saving_path = './assets/downloads/'
    src_uri = f'gs://{bucket_name}/{src_blob.strip('/')}'
    Service.gcs_to_local(src_uri, saving_path, folder)
    return

@app.command()
def ttt(
    src_dir: str = Option(help='Source directory with results from Speech-to-Text V2 request.'),
    dst_file: str = Option(help='Destination filename for storing the results.')
) -> None:
    '''(t)ranscript (t)o (t)ext
    
    This command takes the transcript output from the Speech-to-Text V2 API
    and load its contents into a readable format (txt file).
    '''
    Service.transcript_to_text(src_dir, dst_file)
    return

if __name__ == '__main__':
    app()
