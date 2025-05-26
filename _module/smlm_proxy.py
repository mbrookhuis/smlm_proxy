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
    """
    This function will execute a command and return its output.
    :param cmd:
    :return:
    """
    ret = {}
    cmd_result = __salt__['cmd.run_all'](cmd, python_shell=True)
    if cmd_result['retcode'] != 0:
        ret.update({'success': False, 'message': cmd_result['stdout'], 'error': cmd_result['stderr']})
        log.error(ret['message'])
    else:
        ret['success'] = True
        ret['message'] = cmd_result['stdout']
    return ret

def status():
    """
    Get the status of the SMLM proxy.

    :return:
    """
    cmd = 'mgrpxy status'
    return _execute_command(cmd)

def stop():
    """
    Stop the SMLM proxy.

    :return:
    """
    cmd = 'mgrpxy stop'
    return _execute_command(cmd)

def start():
    """
    start the SMLM proxy.

    :return:
    """
    cmd = 'mgrpxy start'
    return _execute_command(cmd)

def restart():
    """
    Restart the SMLM proxy.

    :return:
    """
    cmd = 'mgrpxy restart'
    return _execute_command(cmd)

