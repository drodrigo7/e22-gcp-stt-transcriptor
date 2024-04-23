# ./modules/utils.py
# ==================================================
# standard
import json
from typing import Any, Dict, List
# --------------------------------------------------

class Utils(object):
    
    @staticmethod
    def json_writer(filename: str, json_dict: Dict[str, Any]) -> None:
        '''Writes an iterable object to a CSV file.
        
        :param filename: Path to the JSON file.
        :type filename: str
        :param json_dict: Dictionary which represents a valid JSON.
        :type json_dict: Dict[str, Any]
        
        :return: None.
        :rtype: None
        '''
        with open(filename, 'w') as jf:
            json.dump(json_dict, jf, indent=2)
        return
    
    @staticmethod
    def transcript_parser(transcript_json: Dict[str, List[Any]]) -> List[str]:
        '''Extracts transcription results into a collection.
        
        :param transcript_json: Dictionary with contents of transcription operation results.
        :type transcript_json: Dict[str, List[Any]]
        
        :return: List containing transcription blocks.
        :rtype: List[str]
        '''
        ftd_results = [r for r in transcript_json['results'] if 'alternatives' in r.keys()]
        return ['{}\n'.format(f['alternatives'][0]['transcript'].strip()) for f in ftd_results]
