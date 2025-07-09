import base64
import logging
import os
import socket
import xmlrpc.client

# Initialize Salt's logger
log = logging.getLogger(__name__)

def __virtual__():
    """
    This function is a Salt convention. It determines if the module should be
    loaded. Returning True means the module will be loaded.
    """
    return True

def _proxy_software_installed():
    """
    Check if the proxy software is installed.
    :return:
    """
    if os.path.isfile("/usr/bin/mgrpxy") and os.path.isfile("/usr/bin/podman"):
        return True
    return False

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

def _check_if_active():
    """
    Check if the proxy is running and if it is already configured.

    :return:
    """
    if _proxy_software_installed():
        ret = status()
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
    intermediate_crt, err = _get_pillar_data("proxy:intermediate_crt", error=False, default_value=[])
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
        os.makedirs(os.path.dirname(file_config), exist_ok=True)
        with open(file_config, 'wb') as f:
            f.write(config_file.data)
    except Exception as file_write_error:
        return {'error': f"Error when writing the file\n{str(file_write_error)}\n{file_config}", 'success': False}
    return {'success': True}

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

    example: salt '<fqdn>' smlm_proxy.status

    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy status'
        return _execute_command(cmd)
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret


def stop():
    """
    Stop the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.stop

    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy stop'
        return _execute_command(cmd)
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret

def start():
    """
    start the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.start

    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy start'
        return _execute_command(cmd)
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret

def restart():
    """
    Restart the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.restart

    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy restart'
        return _execute_command(cmd)
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret

def clearcaches():
    """
    clear the caches of the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.clearcaches

    :return:
    """
    if _proxy_software_installed():
        cmd = 'mgrpxy stop'
        result = _execute_command(cmd)
        if not result['success']:
            return result
        cmd = 'rm -rf /var/lib/containers/storage/volumes/uyuni-proxy-squid-cache/_data/*'
        result = _execute_command(cmd)
        if not result['success']:
            return result
        cmd = 'mgrpxy start'
        result = _execute_command(cmd)
        if not result['success']:
            return result
    else:
        ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
        log.error(ret['message'])
        return ret
    return {'success': True, 'message': "cache of proxy cleared"}

def install(internet_access=False, install_when_missing=True, cert_self_signed=False):
    """
    configure the SMLM proxy.

    example: salt '<fqdn>' smlm_proxy.install

    :param internet_access: When True, when server has internet access. The image from register.suse.com will be used.
    :param install_when_missing: When True, software will be installed when missing
    :param cert_self_signed: When True, self-signed certificate will be used. Currently not implemented!!!!
    :return:
    """

    # self-signed certificates is currently not supported. Will be added later
    if cert_self_signed:
        ret = {'success': False, 'message': "Using self-signed certificate is currently not supported when using"
                                            "this solution. Please follow the official documentation"}
        return ret

    # check if proxy is already running
    ret = _check_if_active()
    if ret['success']:
        ret = {'success': False, 'message': "Proxy already running"}
        return ret

    # configure the proxy
    ret = _check_parameters()
    if not ret["success"]:
        return ret

    # check if podman and mgrpxy are installed
    # when install_when_missing is True install the software when missing. Otherwise, write an error.
    os_finger = __salt__['grains.get']('osfinger')
    if not _proxy_software_installed():
        if install_when_missing:
            ret = _proxy_software_install(internet_access, os_finger)
            if ret["success"]:
                if "sle micro" in os_finger.lower():
                    return ret
            else:
                return ret
        else:
            ret = {'success': False, 'message': "SMLM Proxy software in not installed"}
            log.error(ret['message'])
            return ret

    # configure extra disk
    ret = _get_config()
    if not ret["success"]:
        return ret
    # configure extra disk

    extra_disk, _ = _get_pillar_data("proxy:extradisk", error=False, default_value="")
    ret = _execute_command(f"mgr-storage-proxy {extra_disk}")
    if not ret["success"]:
        return ret

    # start the proxy
    ret = _execute_command("mgrpxy install podman /etc/uyuni/config.tar.gz")
    if not ret["success"]:
        return ret

    ret = {'success': True, 'message': "SMLM Proxy successful installed"}
    return ret




