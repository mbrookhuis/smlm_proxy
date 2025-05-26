# /srv/salt/_modules/file_generator.py

import os
import logging

log = logging.getLogger(__name__)

def generate_and_store(filename, content, directory='/tmp'):
    '''
    Generates a file with the given content and stores it on the minion.

    Args:
        filename (str): The name of the file to create (e.g., 'my_data.txt').
        content (str): The content to write to the file.
        directory (str, optional): The directory where the file will be stored.
                                   Defaults to '/tmp'.

    Returns:
        dict: A dictionary indicating success or failure, and the file path.

    CLI Example:
        salt 'minion_id' file_generator.generate_and_store my_test_file.txt "Hello from Salt!"
        salt 'minion_id' file_generator.generate_and_store another_file.log "This is a log entry." directory=/var/log
    '''
    if not isinstance(filename, str) or not filename:
        return {'result': False, 'comment': 'Filename must be a non-empty string.'}
    if not isinstance(content, str):
        return {'result': False, 'comment': 'Content must be a string.'}
    if not isinstance(directory, str) or not directory:
        return {'result': False, 'comment': 'Directory must be a non-empty string.'}

    # Ensure the directory exists
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755)
            log.info('Created directory: %s', directory)
    except OSError as e:
        log.error('Failed to create directory %s: %s', directory, e)
        return {'result': False, 'comment': f'Failed to create directory {directory}: {e}'}

    file_path = os.path.join(directory, filename)

    try:
        with open(file_path, 'w') as f:
            f.write(content)
        log.info('Successfully generated file: %s', file_path)
        return {
            'result': True,
            'comment': f'File successfully generated at {file_path}',
            'file_path': file_path
        }
    except IOError as e:
        log.error('Failed to write to file %s: %s', file_path, e)
        return {
            'result': False,
            'comment': f'Failed to generate file at {file_path}: {e}'
        }
    except Exception as e:
        log.error('An unexpected error occurred while generating file %s: %s', file_path, e)
        return {
            'result': False,
            'comment': f'An unexpected error occurred: {e}'
        }
