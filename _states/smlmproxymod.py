# smlmproxymod.py
# This is a custom Salt State module.
#
# To use this module:
# 1. Place this file in your Salt master's `_states` directory (e.g., /srv/salt/_states/).
# 2. Sync the modules to your minions: `salt '*' saltutil.sync_states`
#    or `salt '*' saltutil.sync_all`
# 3. Now you can use it in your SLS files.

import os
import logging

# It's good practice to set up a logger for your module
log = logging.getLogger(__name__)

__virtualname__ = 'smlmproxy' # This is how you'll call the state in SLS files (e.g., mystate.my_action_one)

def __virtual__():
    """
    Only load if the mymodule execution module is available.
    This is an optional step, but good practice if your state module
    depends on a custom execution module. For this example, we'll
    assume it's always available or doesn't have such dependencies.
    You could also check for other conditions, e.g., OS type.
    """
    # Example: return False, "The mymodule execution module not found" if not __salt__['mymodule.check_dependency']()
    return __virtualname__

def _execute_command(cmd):
    ret = {}
    cmd_result = __salt__['cmd.run_all'](cmd, python_shell=True)
    if cmd_result['retcode'] != 0:
        ret.update({'success': False, 'message': cmd_result['stdout'], 'error': cmd_result['stderr']})
        log.error(ret['message'])
    else:
        ret['success'] = True
        ret['message'] = cmd_result['stdout']
    return ret

def _status_proxy():
    cmd = 'mgrpxy status'
    return _execute_command(cmd)


def started(name, error_when_running=False):
    """
    Starting the SMLM proxy.

    :param name: The unique ID for this state.
    :param error_when_running: When set to True, an error is generated when there is an attempt to start the proxy

    Example state file:
    proxy-started:
      smlmproxy.started:
        - name: proxy

    """
    ret = {
        'name': name,
        'changes': {},
        'result': False, # Default to False, set to True on success
        'comment': ''
    }

    log.debug(f"Executing smlmproxy.started for {name}")
    log.debug(f"Parameters received: error_when_running='{error_when_running}'")

    # --- Test Mode (dry-run) ---
    if __opts__['test']:
        ret['result'] = None # None indicates test mode success, no changes made
        ret['comment'] = f"SMLM Proxy running on this server would have beem started."
        return ret

    # --- Actual Action Logic ---
    try:
        status_proxy = _status_proxy()['success']
        if status_proxy:
            if error_when_running:
                ret['comment'] = "Error: proxy is already running."
                ret['result'] = False
            else:
                ret['comment'] = "No action needed, proxy is already running."
                ret['result'] = True
        else:
            start_proxy = _execute_command("mgrpxy start")
            if start_proxy["success"]:
                ret['changes'] =  {'old': "proxy not running", 'new': "proxy running"}
                ret['result'] = True
            else:
                ret['comment'] = f"Proxy started failed with error {start_proxy}"
                ret['result'] = False
    except Exception as e:
        ret['comment'] = f"Error in started: {str(e)}"
        ret['result'] = False
        log.error(f"Error in smlm_proxy.started: {e}", exc_info=True)
    return ret

def stopped(name):
    """
    Stopping the SMLM proxy.

    :param name: The unique ID for this state.

    Example state file:
    proxy-stopped:
      smlmproxy.stopped:
        - name: proxy
    """
    ret = {
        'name': name,
        'changes': {},
        'result': False, # Default to False, set to True on success
        'comment': ''
    }

    log.debug(f"Executing smlmproxy.stopped for {name}")

    # --- Test Mode (dry-run) ---
    if __opts__['test']:
        ret['result'] = None # None indicates test mode success, no changes made
        ret['comment'] = f"SMLM Proxy would have been stopped on this server."
        return ret

    # --- Actual Action Logic ---
    try:
        status_proxy = _status_proxy()['success']
        if status_proxy:
            stop_proxy = _execute_command("mgrpxy stop")
            if stop_proxy["success"]:
                ret['changes'] =  {'old': "proxy running", 'new': "proxy not running"}
                ret['result'] = True
            else:
                ret['comment'] = f"Proxy stop failed with error {stop_proxy}"
                ret['result'] = False
        else:
            ret['comment'] = "Proxy is already stopped."
            ret['result'] = True
    except Exception as e:
        ret['comment'] = f"Error in started: {str(e)}"
        ret['result'] = False
        log.error(f"Error in smlm_proxy.started: {e}", exc_info=True)
    return ret

def restart(name):
    """
    Restarting the SMLM proxy.

    :param name: The unique ID for this state.

    Example state file:
    proxy-restart:
      smlmproxy.restart:
        - name: proxy
    """
    ret = {
        'name': name,
        'changes': {},
        'result': False, # Default to False, set to True on success
        'comment': ''
    }

    log.debug(f"Executing smlmproxy.restart for {name}")

    # --- Test Mode (dry-run) ---
    if __opts__['test']:
        ret['result'] = None # None indicates test mode success, no changes made
        ret['comment'] = f"SMLM Proxy would have been restart on this server."
        return ret

    # --- Actual Action Logic ---
    try:
        status_proxy = _status_proxy()['success']
        if status_proxy:
            stop_proxy = _execute_command("mgrpxy stop")
            if not stop_proxy["success"]:
                ret['comment'] = f"Proxy stop failed with error {stop_proxy}"
                ret['result'] = False
                return ret
        start_proxy = _execute_command("mgrpxy start")
        if start_proxy["success"]:
            ret['changes'] =  {'old': "proxy running", 'new': "proxy restarted"}
            ret['result'] = True
        else:
            ret['comment'] = f"Proxy started failed with error {start_proxy}"
            ret['result'] = False
    except Exception as e:
        ret['comment'] = f"Error in started: {str(e)}"
        ret['result'] = False
        log.error(f"Error in smlm_proxy.started: {e}", exc_info=True)
    return ret
