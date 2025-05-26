# -*- coding: utf-8 -*-
'''
Custom execution module for generating files and handling binary output.

This module provides a function `generate_and_store_files` that creates
two types of files on the Salt minion:
1. A text file with content dynamically generated using pillar data and minion grains.
2. A binary file whose content is the raw output of an external command.

Pillar data is used to define file paths, text content prefixes, and the
external command to execute.
'''

import logging
import os

# Initialize Salt's logger
log = logging.getLogger(__name__)

def __virtual__():
    '''
    This function is a Salt convention. It determines if the module should be
    loaded. Returning True means the module will be loaded.
    '''
    return True

def generate_and_store_files(
        binary_output_path=None,
        text_output_path=None,
        text_content_prefix=None,
        external_binary_command=None
):
    '''
    Generates a text file and a binary file on the minion's filesystem.

    The text file's content is constructed using a prefix from pillar data
    and the minion's ID.
    The binary file's content is obtained by executing an external command
    and capturing its raw binary standard output.

    :param binary_output_path: The full path where the binary file should be saved.
                                If not provided, it defaults to the value from
                                the 'my_app:binary_output_path' pillar.
    :param text_output_path: The full path where the text file should be saved.
                             If not provided, it defaults to the value from
                             the 'my_app:text_output_path' pillar.
    :param text_content_prefix: A prefix string to be used in the text file's content.
                                If not provided, it defaults to the value from
                                the 'my_app:text_content_prefix' pillar.
    :param external_binary_command: The shell command to execute to generate
                                    the binary data. Its stdout will be saved.
                                    If not provided, it defaults to the value from
                                    the 'my_app:external_binary_command' pillar.
    :return: A dictionary indicating the success or failure of the operation,
             along with a message and the paths of any files generated.
    '''
    ret = {'success': False, 'message': '', 'files_generated': {}}

    # Fetch parameters from pillar if they were not provided as direct arguments
    # __pillar__ is a special Salt dunder variable that provides access to pillar data.
    binary_output_path = binary_output_path or __pillar__.get('my_app:binary_output_path')
    text_output_path = text_output_path or __pillar__.get('my_app:text_output_path')
    text_content_prefix = text_content_prefix or __pillar__.get('my_app:text_content_prefix')
    external_binary_command = external_binary_command or __pillar__.get('my_app:external_binary_command')

    # Validate that all necessary parameters are available
    if not all([binary_output_path, text_output_path, text_content_prefix, external_binary_command]):
        missing_params = []
        if not binary_output_path: missing_params.append('binary_output_path')
        if not text_output_path: missing_params.append('text_output_path')
        if not text_content_prefix: missing_params.append('text_content_prefix')
        if not external_binary_command: missing_params.append('external_binary_command')

        ret['message'] = (f"Missing one or more required parameters (from arguments or pillar): "
                          f"{', '.join(missing_params)}. Please ensure your pillar is configured correctly.")
        log.error(ret['message'])
        return ret

    # --- Step 1: Generate and store the text file ---
    try:
        # Get the minion's ID using Salt's grains module
        minion_id = __salt__['grains.get']('id')
        # Get current time using Salt's time module for dynamic content
        current_time = __salt__['time.strftime']('%Y-%m-%d %H:%M:%S')

        text_content = (
            f"{text_content_prefix} {minion_id}\n\n"
            f"This file was created on: {current_time}\n"
            f"A simple configuration example."
        )

        # Use Salt's file.write function to write the text content to the specified path.
        # This function handles creating directories if they don't exist.
        __salt__['file.write'](text_output_path, text_content)
        ret['files_generated']['text_file'] = text_output_path
        log.info(f"Successfully generated text file at: {text_output_path}")

    except Exception as e:
        ret['message'] = f"Failed to generate text file '{text_output_path}': {e}"
        log.error(ret['message'])
        return ret

    # --- Step 2: Execute external command and save its binary output ---
    try:
        log.info(f"Attempting to execute external command: '{external_binary_command}'")

        # Use Salt's cmd.run_all to execute the command.
        # IMPORTANT: `decode=False` is crucial here to ensure the stdout is returned
        # as raw bytes, preventing corruption of binary data by string decoding attempts.
        cmd_result = __salt__['cmd.run_all'](external_binary_command, python_shell=True, decode=False)

        if cmd_result['retcode'] != 0:
            # If the command failed, log stderr and return an error.
            stderr_output = cmd_result['stderr'].decode('utf-8', errors='ignore')
            ret['message'] = (f"External command failed with return code {cmd_result['retcode']}. "
                              f"Stderr: {stderr_output}")
            log.error(ret['message'])
            return ret

        # The stdout from the command should now be in raw bytes
        binary_data = cmd_result['stdout']

        if not isinstance(binary_data, bytes):
            # This is a critical warning. If `decode=False` didn't work as expected
            # and we received a string, the binary data is likely corrupted.
            log.warning(f"cmd.run_all returned type {type(binary_data)} instead of bytes for binary command. "
                        "Binary data might be corrupted. Attempting to re-encode (lossy for non-text data).")
            # Fallback: try to encode it back to bytes, though this is problematic for arbitrary binary
            binary_data = str(binary_data).encode('latin-1', errors='ignore')

        # Write the binary data to the specified file path in binary write mode ('wb')
        try:
            # Ensure the directory exists before writing the file
            os.makedirs(os.path.dirname(binary_output_path), exist_ok=True)
            with open(binary_output_path, 'wb') as f:
                f.write(binary_data)
            ret['files_generated']['binary_file'] = binary_output_path
            log.info(f"Successfully saved binary file at: {binary_output_path}")
        except Exception as file_write_error:
            ret['message'] = (f"Failed to write binary data to file '{binary_output_path}': "
                              f"{file_write_error}")
            log.error(ret['message'])
            return ret

    except Exception as e:
        ret['message'] = f"Failed during external command execution or binary file handling: {e}"
        log.error(ret['message'])
        return ret

    # If all steps complete successfully
    ret['success'] = True
    ret['message'] = "All files generated successfully."
    return ret
