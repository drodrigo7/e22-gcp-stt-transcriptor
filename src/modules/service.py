# ./modules/service.py
# ==================================================
# standard
import time, contextlib, pathlib, json
# requirements
from moviepy.editor import VideoFileClip
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.longrunning.operations_pb2 import GetOperationRequest
from google.protobuf.json_format import MessageToJson
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types.cloud_speech import (
    BatchRecognizeFileMetadata,
    BatchRecognizeRequest,
    GcsOutputConfig,
    RecognitionOutputConfig,
    AutoDetectDecodingConfig,
    RecognitionConfig
)
# defined
from .logger import watcher
from .utils import Utils
# --------------------------------------------------

class Service(object):
    
    @staticmethod
    def retrieve_audio(video_path: str, saving_path: str) -> str:
        '''Extracts audio from a video file (mp4).
        
        :param video_path: Path to video that requires audio extraction.
        :type video_path: str
        :param saving_path: Local folder path for storing downloads.
        :type saving_path: str
        
        :return: The audio file location.
        :rtype: str
        '''
        video = VideoFileClip(video_path)
        with contextlib.closing(video):
            audio = video.audio
            filepath = '{}/{}.wav'.format(saving_path.strip('/'), video_path.split('/').pop())
            audio.write_audiofile(filepath)
        
        watcher.info('Audio exported to {}'.format(filepath))
        return filepath
    
    @staticmethod
    def file_to_gcs(bucket_name: str, src_file: str, blob_name: str) -> str:
        '''Uploads a file to the Google Cloud Storage bucket.
        
        :param bucket_name: Name of the Google Cloud Storage bucket.
        :type bucket_name: str
        :param source_file: Local file path of the file to upload.
        :type source_file: str
        :param blob_name: Name of the file in the bucket after upload.
        :type source_file: str
        
        :return: GCS URI path.
        :rtype: str
        '''
        stg_client = storage.Client()
        with contextlib.closing(stg_client):
            bucket = stg_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(src_file)
        
        uri_name = 'gs://{}/{}'.format(blob.bucket.name, blob.name)
        watcher.info('File {} uploaded to: {}.'.format(src_file, uri_name))
        return uri_name
    
    @staticmethod
    def dynamic_batch_transcription(project_id: str, src_uri: str, dst_uri: str, tracking_file: str) -> None:
        '''Transcribes audio from a Google Cloud Storage URI
        using dynamic batching on batch recognition for long
        audios.
        
        :param project_id: The Google Cloud project ID.
        :type project_id: str
        :param src_uri: The Google Cloud Storage URI.
        :type src_uri: str
        :param dst_uri: The Google Cloud Storage URI for Speech-to-Text output.
        :type dst_uri: str
        
        :return: None.
        :rtype: None
        '''
        speechv2_client = SpeechClient(
            client_options=ClientOptions(api_endpoint='us-central1-speech.googleapis.com')
        )
        file_metadata = BatchRecognizeFileMetadata(uri=src_uri)
        processing_strat = BatchRecognizeRequest.ProcessingStrategy.DYNAMIC_BATCHING
        recog_output_cfg = RecognitionOutputConfig(gcs_output_config=GcsOutputConfig(uri=dst_uri))
        
        config = RecognitionConfig(
            auto_decoding_config=AutoDetectDecodingConfig(),
            language_codes=['es-US'],
            model='chirp'
        )
        
        request = BatchRecognizeRequest(
            recognizer='projects/{}/locations/us-central1/recognizers/_'.format(project_id),
            config=config,
            files=[file_metadata],
            recognition_output_config=recog_output_cfg,
            processing_strategy=processing_strat,
        )
        
        long_operation = speechv2_client.batch_recognize(request=request)
        operation_name = long_operation.operation.name
        
        time.sleep(10)
        completed = long_operation.done()
        
        csv_row = json.dumps({'completed': completed, 'name': operation_name})
        Utils.csv_writer(tracking_file, [csv_row])
        
        if completed:
            watcher.info('Operation completed: {}', operation_name)
            return
        watcher.info('Operation in progress: {}', operation_name)
        return
    
    @staticmethod
    def retrieve_transcript(operation_name: str, tracking_file: str) -> None:
        '''Retrieves the status of a GCP operation by its name.
        
        :param operation_name: Operation ID for a long running operation from Speech-to-Text V2.
        :type operation_name: str
        :param tracking_file: File to write status for operations.
        :type tracking_file: str
        
        :return: None.
        :rtype: None
        '''
        speechv2_client = SpeechClient(
            client_options=ClientOptions(api_endpoint='us-central1-speech.googleapis.com')
        )
        ops_response = speechv2_client.get_operation(request=GetOperationRequest(name=operation_name))
        if ops_response.done:
            csv_row = json.dumps({
                'completed' : ops_response.done,
                'name'      : ops_response.name,
                'metadata'  : json.loads(MessageToJson(ops_response.metadata)),
                'response'  : json.loads(MessageToJson(ops_response.response))
            })
            Utils.csv_writer(tracking_file, [csv_row])
            watcher.info('Operation completed. Metadata exported to: {}'.format(tracking_file))
            return
        
        watcher.info('Operation pending: {}'.format(ops_response.name))
        return
    
    @staticmethod
    def gcs_to_local(src_uri: str, saving_path: str, folder: bool) -> str:
        '''Downloads a blob from GCS to the directory.
        
        :param src_uri: GCS URI path of blob.
        :type src_uri: str
        :param saving_path: Local folder path for storing downloads.
        :type saving_path: str
        :param folder: Flag that indicates if URI is partial (folder).
        :type folder: bool
        
        :return: Local path for the downloaded file.
        :rtype: str
        '''
        spt_uri = src_uri.strip('/').replace('gs://', '').split('/')
        filepath = '{}/{}'.format(saving_path.strip('/'), spt_uri[-1])
        stg_client = storage.Client()
        
        if folder:
            pathlib.Path(filepath).mkdir(parents=True, exist_ok=True)
            splt_uri = src_uri.replace('gs://', '').split('/')
            
            bucket_name, folder_name = splt_uri.pop(0), '/'.join(splt_uri)
            bucket_blobs = [b for b in stg_client.list_blobs(bucket_name, prefix=folder_name)]
            
            for b in bucket_blobs:
                b.download_to_filename('{}/{}'.format(filepath, b.name.split('/')[-1]))
            
            watcher.info('Elements from "{}" downloaded to: {}.'.format(src_uri, filepath))
            return filepath
        
        with contextlib.closing(stg_client):
            with open(filepath, 'wb') as sf:
                _ = stg_client.download_blob_to_file(src_uri, sf)
        
        watcher.info('File "{}" downloaded to: {}.'.format(src_uri, filepath))
        return filepath
    
    @staticmethod
    def transcript_to_text(src_file: str, dst_file: str) -> str:
        '''Read result from Speech-to-Text V2 request and writes a text file.
        
        :param src_file: Source file with results from Speech-to-Text V2 request.
        :type src_file: str
        :param dst_file: Destination filename for storing the results.
        :type dst_file: str
        
        :return: Local path to file with Speech-to-Text V2 output.
        :rtype: str
        '''
        jf_params = dict(file=src_file, mode='r', encoding='utf-8')
        tf_params = dict(file=dst_file, mode='w', encoding='utf-8')
        
        with open(**jf_params) as jf, open(**tf_params) as tf:
            transcript = json.load(jf)
            linewriter = lambda r: '{}\n'.format(r['alternatives'][0]['transcript'].strip())
            tf.writelines([linewriter(r) for r in transcript['results']])
        
        watcher.info('Transcription text exported at: {}'.format(dst_file))
        return dst_file
