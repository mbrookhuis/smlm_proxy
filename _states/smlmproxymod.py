# smlmproxymod.py
# This is a custom Salt State module.
#
# To use this module:
# 1. Place this file in your Salt master's `_states` directory (e.g., /srv/salt/_states/).
# 2. Sync the modules to your minions: `salt '*' saltutil.sync_states`
#    or `salt '*' saltutil.sync_all`
# 3. Now you can use it in your SLS files.
import base64
import os
import logging
import socket
import xmlrpc.client

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

def _proxy_software_installed():
    """
    Check if the proxy software is installed.
    :return:
    """
    if os.path.isfile("/usr/bin/mgrpxy"):
        return True
    return False

def _execute_command(cmd):
    """
    Execute the given command

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

def _status_proxy():
    """
    Check if the proxy is running.
    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy status'
        return _execute_command(cmd)
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret

def _check_if_active():
    """
    Check if the proxy is running and if it is already configured.

    :return:
    """
    ret = _status_proxy()
    if ret['success']:
        return {'success': True, 'message': "Proxy already running"}
    if os.path.isfile("/etc/uyuni/proxy/config.yaml") or os.path.isfile("/etc/uyuni/proxy/httpd.yaml") or os.path.isfile("/etc/uyuni/proxy/ssh.yaml"):
        return {'success': True, 'message': "Proxy already configured"}
    return {'success': False, 'message': "Proxy not configured"}

def _check_parameters():
    """
    Check if the certificate date is available and if this is the case,
    create the config file for the proxy.
    :return:
    """
    root_crt, err = _get_pillar_data("proxy:root_crt")
    if err:
        log.error(err)
        return {'error': err, 'success': False}
    server_crt, err = _get_pillar_data("proxy:server_crt")
    if err:
        log.error(err)
        return {'error': err, 'success': False}
    server_key, err = _get_pillar_data("proxy:server_key")
    if err:
        log.error(err)
        return {'error': err, 'success': False}
    smlm_cred, err = _get_pillar_data("proxy:smlmcred")
    if err:
        log.error(err)
        return {'error': err, 'success': False}
    email, err = _get_pillar_data("proxy:email")
    if err:
        log.error(err)
        return {'error': err, 'success': False}
    return {'success': True}

def _login_smlm():
    """
    Login to SMLM
    :return: error, client connections and session key
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect_ex((__salt__['grains.get']('master'), 443))
    except Exception:
        error = f"Unable to login to SUSE Manager server {__salt__['grains.get']('master')}."
        return error, None, None
    client = xmlrpc.client.Server("https://" + __salt__['grains.get']('master') + "/rpc/api")
    smlm_cred, err = _get_pillar_data("proxy:smlmcred")
    credentials = base64.b64decode(smlm_cred).decode('utf-8')
    try:
        session = client.auth.login(credentials.split(':')[0], credentials.split(':', 1)[1])
    except Exception:
        error = f"Unable to login to SUSE Manager server {__salt__['grains.get']('master')}."
        return error, None, None
    return None, client, session

def _get_config():
    # login to SMLM
    err, client, session = _login_smlm()
    if err:
        return {'error': err, 'success': False}

    # collecting all needed parameters
    root_crt, _ = _get_pillar_data("proxy:root_crt")
    server_crt, _ = _get_pillar_data("proxy:server_crt")
    server_key, _ = _get_pillar_data("proxy:server_key")
    email, _ = _get_pillar_data("proxy:email")
    proxy_port, _ = _get_pillar_data("proxy:proxyport", error=False, default_value=8022)
    max_cache, err = _get_pillar_data("proxy:maxcache", error=False, default_value=2048)
    intermediate_crt, err = _get_pillar_data("proxy:intermediate.crt", error=False, default_value=[])
    proxy_name = __salt__['grains.get']('fqdn')
    smlm = __salt__['grains.get']('master')

    intermediate = []
    for x in intermediate_crt:
        intermediate.append(x)

    # ask smlm to create the config file
    try:
        config_file = client.proxy.container_config(session, proxy_name, proxy_port, smlm, max_cache, email, root_crt, intermediate, server_crt, server_key)
    except Exception:
        return {'error': "Unable to get config file", 'success': False}
    # write config file to /etc/uyuni/proxy
    file_config="/etc/uyuni/config.tar.gz"
    try:
        # Ensure the directory exists before writing the file
        #os.makedirs(os.path.dirname(file_config), exist_ok=True)
        with open(file_config, 'wb') as f:
            f.write(config_file.data)
    except Exception as file_write_error:
        return {'error': f"Error when writing the file\n{str(file_write_error)}\n{file_config}", 'success': False}
    return {'success': True}

def _proxy_software_install(internet_access, os_finger):
    """
    Install proxy software.

    :param internet_access:
    :return:
    """
    cpu_arch = __salt__['grains.get']('cpuarch')

    if internet_access:
        packages = f"podman uyuni-storage-setup-proxy mgrpxy* mgrctl*"
    else:
        packages = f"podman uyuni-storage-setup-proxy mgrpxy* mgrctl* suse-manager-5.0-{cpu_arch}-proxy-*"
    if "sle micro" in os_finger.lower():
        ret = _execute_command(f"transactional-update -i pkg in {packages}")
        if ret['success']:
            _execute_command("systemctl enable podman")
            ret['message'] = "Software installed. Reboot server and re-issue the same command to install proxy"
        return ret
    else:
        ret=_execute_command(f"zypper -n in {packages}")
        if ret['success']:
            ret1 = _execute_command("systemctl enable --now podman")
            return ret1
        else:
            return ret

def _get_pillar_data(pillar_key, error=True, default_value=None):
    """
    Get the value of the given pillar key. Return None if it isn't found or if it is empty.

    :param pillar_key:
    :return: value of the pillar key
    """
    data = __salt__['pillar.get'](pillar_key)

    if data is None or not data:
        if error:
            error = (f"Pillar keys {pillar_key} is empty or not present. Please fix pillar data for "
                     f"server {__salt__['grains.get']('fqdn')}.")
            return None, error
        else:
            if default_value:
                return default_value, None
    return data, None

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

def installed(name, internet_access=False, install_when_missing=True, cert_self_signed=False):
    """
    configure the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.install

    :param name: Default is proxy.
    :param internet_access: When True, when server has internet access. The image from register.suse.com will be used.
    :param install_when_missing: When True, software will be installed when missing
    :param cert_self_signed: When True, self-signed certificate will be used. Currently not implemented!!!!
    :return:
    """

    ret = {
        'name': name,
        'changes': {},
        'result': False, # Default to False, set to True on success
        'comment': ''
    }

    log.debug(f"Executing smlmproxy.installed for {name}")
    log.debug(f"Parameters received: internet_access='{internet_access}', install_when_missing='{install_when_missing}'"
              f"cert_self_signed='{cert_self_signed}', ")

    # --- Test Mode (dry-run) ---
    if __opts__['test']:
        ret['result'] = None # None indicates test mode success, no changes made
        ret['comment'] = f"SMLM Proxy would have been installed on this server."
        return ret

    try:
        # self-signed certificates is currently not supported. Will be added later
        if cert_self_signed:
            ret['result'] = False
            ret['comment'] = ("Using self-signed certificate is currently not supported when using this solution. "
                              "Please follow the official documentation")
            return ret

        # check if proxy is already running
        result = _check_if_active()
        if result['success']:
            ret['result'] = False
            ret['comment'] = "Proxy already running"
            return ret

        # configure the proxy
        result = _check_parameters()
        if not result["success"]:
            ret['result'] = False
            ret['comment'] = result["error"]
            return ret

        # check if podman and mgrpxy are installed
        # when install_when_missing is True install the software when missing. Otherwise, write an error.
        os_finger = __salt__['grains.get']('osfinger')
        if not _proxy_software_installed():
            if install_when_missing:
                result = _proxy_software_install(internet_access, os_finger)
                if result["success"]:
                    if "sle micro" in os_finger.lower():
                        ret['result'] = True
                        ret['comment'] = result["message"]
                        ret['changes'] = {'old': 'proxy not installed', 'new': "proxy installed, but not configured"}
                        return ret
                else:
                    ret['result'] = False
                    ret['comment'] = result["message"]
                    return ret
            else:
                ret['result'] = False
                ret['comment'] = "SMLM Proxy software in not installed"
                return ret

        # configure extra disk
        result = _get_config()
        if not result["success"]:
            ret['result'] = False
            ret['comment'] = result["error"]
            return ret
        # configure extra disk

        extra_disk, _ = _get_pillar_data("proxy:extradisk", error=False, default_value="")
        result = _execute_command(f"mgr-storage-proxy {extra_disk}")
        if not result["success"]:
            ret['result'] = False
            ret['comment'] = result["error"]
            return ret

        # start the proxy
        result = _execute_command("mgrpxy install podman /etc/uyuni/config.tar.gz")
        if not result["success"]:
            ret['result'] = False
            ret['comment'] = result["error"]
            return ret

    except Exception as e:
        ret['comment'] = f"Error in installed: {str(e)}"
        ret['result'] = False
        log.error(f"Error in smlm_proxy.installed: {e}", exc_info=True)

    ret['changes'] =  {'old': "proxy not installed", 'new': "proxy installed, configured and running"}
    ret['result'] = True
    return ret
