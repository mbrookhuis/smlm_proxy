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

def _execute_command(cmd):
    ret = {}
    cmd_result = __salt__['cmd.run_all'](cmd, python_shell=True)
    if cmd_result['retcode'] != 0:
        ret.update({'success': False, 'message': cmd_result['stdout'], 'error': cmd_result['stderr']})
        # If the command failed, log stderr and return an error.
        # ret['message'] = cmd_result['stderr']
        log.error(ret['message'])
    else:
        ret['success'] = True
        ret['message'] = cmd_result['stdout']
    return ret

def status():
    cmd = 'mgrpxy status'
    return _execute_command(cmd)

def stop():
    cmd = 'mgrpxy stop'
    return _execute_command(cmd)

def start():
    cmd = 'mgrpxy start'
    return _execute_command(cmd)

def restart():
    cmd = 'mgrpxy restart'
    return _execute_command(cmd)

