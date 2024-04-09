# ./modules/utils.py
# ==================================================
# standard
import csv
from typing import Iterable
# --------------------------------------------------

class Utils(object):
    
    @staticmethod
    def csv_writer(filename: str, data: Iterable) -> None:
        '''Writes an iterable object to a CSV file.
        
        :param filename: Path to the CSV file.
        :type filename: str
        :param data: Iterable object to write as CSV row.
        :type data: Iterable
        
        :return: None.
        :rtype: None
        '''
        with open(filename, 'a', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(data)
        return
