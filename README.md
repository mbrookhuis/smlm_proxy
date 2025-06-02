# smlm_proxy
salt module to manage SUSE Multi Linux Manager proxy via salt

## Preparation

### Installation
To use the execution and salt modules perform the following actions.
* copy _module/smlm_proxy.cp to the /srv/salt/_module directory
```bash
mgrctl cp smlm_proxy.py server:/srv/salt/_module
```
* copy _status/smlmproxymod.cp to the /srv/salt/_states directory
```bash
mgrctl cp _states/smlmproxymod.py server:/srv/salt/_states
```
* the modules will not be present after copying. Perform a highstate or execute the following command:
```bash
mgrctl exec -ti 'salt "<proxy fqdn>" saltutil.sync_all'
```

### Needed pillar file per proxy
Both the executions and the state commands are expecting pillar information to be present.
For this create in /srv/pillar a sls file (e.g. with the name proxy_<proxy hostname>). The following should be present:

```yaml
{% import_text "/srv/pillar/certs/<smlm proxy certificate>" as server_crt %}
{% import_text "/srv/pillar/certs/<smlm proxy key>" as server_key %}
{% import_text "/srv/pillar/certs/<rootCA certificate>" as root_crt %}
{% import_text "/srv/pillar/certs/intermediate_1.crt" as intermediate_crt_1 %}

proxy:
smlmcred: <credentials of SMLM in the format user:password and then base64 encoded>
server_crt: {{ server_crt | json }}
server_key: {{ server_key | json }}
root_crt: {{ root_crt | json }}
proxyport: 8022   # this is the default, define another value when needed
maxcache: 2048   # this is the default, define another value when needed
email: <mail address, this is needed for the config, but is not used>
intermediate_crt:    # this is optional. do not define when this is not needed.
  - {<intermediate_crt_1}
  - {<intermediate_crt_2}
  - ... 
  - {<intermediate_crt_n}

```

### Certificates
Create or copy the needed certificate to /srv/pillar/certs. If needed, you can set the hostname in the certificate or create a separate directory 
for each proxy server. Adjust the link in the above-mentioned file. 

If intermediates are needed. Please create a separate file for each intermediate certificate and add them in the above-mentioned file. 
The API call is not able to handle files with multiple certificates.

Currently, these salt modules don't support self-signed certificates. This will be added later.

## Execution modules

The following modules are present:
* smlm_proxy.status       --> this will show the status of the proxy
* smlm_proxy.start        --> this will start the proxy
* smlm_proxy.restart      --> this will stop of the proxy
* smlm_proxy.stop         --> this will restart of the proxy
* smlm_proxy.clearcaches  --> this will clear the caches of the proxy
* smlm_proxy.install      --> this will install the proxy when not present already.

For the option install the following parameters are present: 
* internet_access: When True, when server has internet access. The image from register.suse.com will be used.
* install_when_missing: When True, software will be installed when missing
* cert_self_signed: When True, self-signed certificate will be used. Currently not implemented!!!!

### example
The example assumes that the command is issued from the SMLM container. When running the command local on 
the proxy, replace 'salt' with 'salt-call' or 'venv-salt-call', depending on what salt flavor has been installed.

To check the status of the mbsumapro502:
```bash
uyuni-server:/srv/salt # salt 'mbsumapro502.mb.int' smlm_proxy.status
mbsumapro502.mb.int:
    ----------
    message:
        1:34PM INF Welcome to mgrpxy
        1:34PM INF Executing command: status
        1:34PM WRN Failed to find home directory error="$HOME is not defined"
        * uyuni-proxy-httpd.service - Uyuni proxy httpd container service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-httpd.service; disabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-httpd.service.d
                     `-generated.conf
             Active: active (running) since Mon 2025-06-02 11:38:01 CEST; 1h 56min ago
            Process: 10266 ExecStartPre=/bin/rm -f /run/uyuni-proxy-httpd.pid /run/uyuni-proxy-httpd.ctr-id (code=exited, status=0/SUCCESS)
            Process: 10273 ExecStart=/bin/sh -c /usr/bin/podman run     --conmon-pidfile /run/uyuni-proxy-httpd.pid     --cidfile /run/uyuni-proxy-httpd.ctr-id         --cgroups=no-conmon          --pod-id-file /run/uyuni-proxy-pod.pod-id -d    --replace -dt   -v /etc/uyuni/proxy:/etc/uyuni:ro       -v uyuni-proxy-rhn-cache:/var/cache/rhn     -v uyuni-proxy-tftpboot:/srv/tftpboot    ${HTTPD_EXTRA_CONF} --name uyuni-proxy-httpd    ${UYUNI_IMAGE} (code=exited, status=0/SUCCESS)
           Main PID: 10446 (conmon)
              Tasks: 1
                CPU: 182ms
             CGroup: /system.slice/uyuni-proxy-httpd.service
                     `-10446 /usr/bin/conmon --api-version 1 -c df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5 -u df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5 -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5/userdata -p /run/containers/storage/overlay-containers/df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5/userdata/pidfile -n uyuni-proxy-httpd --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5/userdata/oci-log -t --conmon-pidfile /run/uyuni-proxy-httpd.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg df01c3ee490b2e0db566c69b3c06e23cf1a18d859c72802388ac6487eeeeade5

        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]: WARNING:root:No IPv6 address detected for proxy. If this is single stack IPv4 setup this warning can be ignored
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]: DEBUG:root:Detected ips '192.168.100.52', '' for fqdn mbsumapro502.mb.int
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]: AH00558: httpd-prefork: Could not reliably determine the server's fully qualified domain name, using 10.89.0.3. Set the 'ServerName' directive globally to suppress this message
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [error] [pid 1] ssl_util_stapling.c(149): [client AH02217: ssl_stapling_init_cert: can't retrieve issuer certificate! [subject: CN=mbsumapro502.mb.int,OU=SUSE Consulting,O=SUSE,L=HRL,ST=LI,C=NL / issuer: CN=mb.int,OU=SUSE Consulting,O=SUSE,L=HRL,ST=LI,C=NL / serial: 545C0A0C30B7329783419E18DF47392C72B1D85D / notbefore: May 30 14:47:57 2025 GMT / notafter: Sep  3 14:47:57 2027 GMT]
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [error] [pid 1] ssl_engine_init.c(2041): [client AH02604: Unable to configure certificate mbsumapro502.mb.int:443:0 for stapling
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]: AH00558: httpd-prefork: Could not reliably determine the server's fully qualified domain name, using 10.89.0.3. Set the 'ServerName' directive globally to suppress this message
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [error] [pid 1] ssl_util_stapling.c(149): [client AH02217: ssl_stapling_init_cert: can't retrieve issuer certificate! [subject: CN=mbsumapro502.mb.int,OU=SUSE Consulting,O=SUSE,L=HRL,ST=LI,C=NL / issuer: CN=mb.int,OU=SUSE Consulting,O=SUSE,L=HRL,ST=LI,C=NL / serial: 545C0A0C30B7329783419E18DF47392C72B1D85D / notbefore: May 30 14:47:57 2025 GMT / notafter: Sep  3 14:47:57 2027 GMT]
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [error] [pid 1] ssl_engine_init.c(2041): [client AH02604: Unable to configure certificate mbsumapro502.mb.int:443:0 for stapling
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [notice] [pid 1] prefork.c(965): [client AH00163: Apache/2.4.58 (Linux/SUSE) OpenSSL/3.1.4 mod_wsgi/4.7.1 Python/3.6 configured -- resuming normal operations
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-httpd[10446]:  [Mon Jun 02 09:38:01 2025] [notice] [pid 1] log.c(1591): [client AH00094: Command line: '/usr/sbin/httpd-prefork -D SYSCONFIG -D SSL -C PidFile /run/httpd.pid -C Include /etc/apache2/sysconfig.d//loadmodule.conf -C Include /etc/apache2/sysconfig.d//global.conf -f /etc/apache2/httpd.conf -c Include /etc/apache2/sysconfig.d//include.conf -D FOREGROUND'
        * uyuni-proxy-salt-broker.service - Uyuni proxy Salt broker container service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-salt-broker.service; disabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-salt-broker.service.d
                     `-generated.conf
             Active: active (running) since Mon 2025-06-02 11:38:00 CEST; 1h 56min ago
            Process: 10269 ExecStartPre=/bin/rm -f /run/uyuni-proxy-salt-broker.pid /run/uyuni-proxy-salt-broker.ctr-id (code=exited, status=0/SUCCESS)
            Process: 10274 ExecStart=/bin/sh -c /usr/bin/podman run     --conmon-pidfile /run/uyuni-proxy-salt-broker.pid       --cidfile /run/uyuni-proxy-salt-broker.ctr-id        --cgroups=no-conmon     --pod-id-file /run/uyuni-proxy-pod.pod-id -d    --replace -dt   -v /etc/uyuni/proxy:/etc/uyuni:ro       --name uyuni-proxy-salt-broker      ${UYUNI_IMAGE} (code=exited, status=0/SUCCESS)
           Main PID: 10339 (conmon)
              Tasks: 1
                CPU: 117ms
             CGroup: /system.slice/uyuni-proxy-salt-broker.service
                     `-10339 /usr/bin/conmon --api-version 1 -c 1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed -u 1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed/userdata -p /run/containers/storage/overlay-containers/1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed/userdata/pidfile -n uyuni-proxy-salt-broker --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed/userdata/oci-log -t --conmon-pidfile /run/uyuni-proxy-salt-broker.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg 1644d9c33dff83899afa7b26001a336d625815e69fe2b834d68c26aca401abed

        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,059 [DEBUG   ][RetChannelProxy ][8] Setting socket opt TCP_KEEPALIVE_INTVL to -1 on DEALER
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,059 [DEBUG   ][RetChannelProxy ][8] Setting socket opt CONNECT_TIMEOUT to 0 on DEALER
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,059 [DEBUG   ][PubChannelProxy ][7] Setting socket opt XPUB_VERBOSE to 1 on XPUB
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [DEBUG   ][RetChannelProxy ][8] Setting socket opt RECONNECT_IVL to 100 on DEALER
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [DEBUG   ][PubChannelProxy ][7] Setting socket opt XPUB_VERBOSER to 1 on XPUB
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [DEBUG   ][RetChannelProxy ][8] Setting socket opt HEARTBEAT_IVL to 0 on DEALER
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [DEBUG   ][RetChannelProxy ][8] Setting socket opt HEARTBEAT_TIMEOUT to 0 on DEALER
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [INFO    ][PubChannelProxy ][7] Staring ZMQ proxy on XPUB and XSUB sockets
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [DEBUG   ][RetChannelProxy ][8] Setting up a ROUTER sock on tcp://0.0.0.0:4506
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-salt-broker[10339]: 2025-06-02 09:38:01,060 [INFO    ][RetChannelProxy ][8] Staring ZMQ proxy on ROUTER and DEALER sockets
        * uyuni-proxy-squid.service - Uyuni proxy squid container service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-squid.service; disabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-squid.service.d
                     `-generated.conf
             Active: active (running) since Mon 2025-06-02 11:38:00 CEST; 1h 56min ago
            Process: 10270 ExecStartPre=/bin/rm -f /run/uyuni-proxy-squid.pid /run/uyuni-proxy-squid.ctr-id (code=exited, status=0/SUCCESS)
            Process: 10275 ExecStart=/bin/sh -c /usr/bin/podman run     --conmon-pidfile /run/uyuni-proxy-squid.pid     --cidfile /run/uyuni-proxy-squid.ctr-id         --cgroups=no-conmon          --pod-id-file /run/uyuni-proxy-pod.pod-id -d    --replace -dt   -v /etc/uyuni/proxy:/etc/uyuni:ro       -v uyuni-proxy-squid-cache:/var/cache/squid  ${SQUID_EXTRA_CONF} --name uyuni-proxy-squid    ${UYUNI_IMAGE} (code=exited, status=0/SUCCESS)
           Main PID: 10403 (conmon)
              Tasks: 1
                CPU: 114ms
             CGroup: /system.slice/uyuni-proxy-squid.service
                     `-10403 /usr/bin/conmon --api-version 1 -c 204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb -u 204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb/userdata -p /run/containers/storage/overlay-containers/204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb/userdata/pidfile -n uyuni-proxy-squid --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb/userdata/oci-log -t --conmon-pidfile /run/uyuni-proxy-squid.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg 204ec8bc26f26e4fb6958136b5e878fd5b188d6e9a57864cf1764a812878c4eb

        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 09:38:01 kid1| Completed Validation Procedure
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-squid[10403]:     Validated 0 Entries
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-squid[10403]:     store_swap_size = 0.00 KB
        Jun 02 11:38:02 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 09:38:02 kid1| storeLateRelease: released 0 objects
        Jun 02 12:33:19 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 10:33:19 kid1| Logfile: opening log stdio:/var/cache/squid/netdb.state
        Jun 02 12:33:19 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 10:33:19 kid1| Logfile: closing log stdio:/var/cache/squid/netdb.state
        Jun 02 12:33:19 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 10:33:19 kid1| NETDB state saved; 0 entries, 0 msec
        Jun 02 13:14:58 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 11:14:58 kid1| Logfile: opening log stdio:/var/cache/squid/netdb.state
        Jun 02 13:14:58 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 11:14:58 kid1| Logfile: closing log stdio:/var/cache/squid/netdb.state
        Jun 02 13:14:58 mbsumapro502 uyuni-proxy-squid[10403]: 2025/06/02 11:14:58 kid1| NETDB state saved; 0 entries, 0 msec
        * uyuni-proxy-ssh.service - Uyuni proxy ssh container service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-ssh.service; disabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-ssh.service.d
                     `-generated.conf
             Active: active (running) since Mon 2025-06-02 11:38:00 CEST; 1h 56min ago
            Process: 10271 ExecStartPre=/bin/rm -f /run/uyuni-proxy-ssh.pid /run/uyuni-proxy-ssh.ctr-id (code=exited, status=0/SUCCESS)
            Process: 10276 ExecStart=/bin/sh -c /usr/bin/podman run     --conmon-pidfile /run/uyuni-proxy-ssh.pid       --cidfile /run/uyuni-proxy-ssh.ctr-id   --cgroups=no-conmon          --pod-id-file /run/uyuni-proxy-pod.pod-id -d    --replace -dt   -v /etc/uyuni/proxy:/etc/uyuni:ro       --name uyuni-proxy-ssh          ${UYUNI_IMAGE} (code=exited, status=0/SUCCESS)
           Main PID: 10329 (conmon)
              Tasks: 1
                CPU: 111ms
             CGroup: /system.slice/uyuni-proxy-ssh.service
                     `-10329 /usr/bin/conmon --api-version 1 -c 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06 -u 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06 -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06/userdata -p /run/containers/storage/overlay-containers/69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06/userdata/pidfile -n uyuni-proxy-ssh --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06/userdata/oci-log -t --conmon-pidfile /run/uyuni-proxy-ssh.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06

        Jun 02 11:38:00 mbsumapro502 podman[10276]: 2025-06-02 11:38:00.708220181 +0200 CEST m=+0.085367743 container create 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06 (image=localhost/suse/manager/5.0/x86_64/proxy-ssh:5.0.4, name=uyuni-proxy-ssh, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, com.suse.bci.base.supportlevel=l3, com.suse.lifecycle-url=https://www.suse.com/lifecycle/, com.suse.eula=sle-eula, com.suse.manager.proxy-ssh.supportlevel=l3, com.suse.manager.proxy-ssh.url=https://www.suse.com/products/suse-manager, com.suse.bci.base.created=2025-02-04T09:51:01.275197080Z, com.suse.bci.base.lifecycle-url=https://www.suse.com/lifecycle#suse-linux-enterprise-server-15, com.suse.bci.base.authors=https://github.com/SUSE/bci/discussions, org.opencontainers.image.authors=https://github.com/SUSE/bci/discussions, com.suse.bci.base.disturl=obs://build.suse.de/SUSE:Maintenance:37326/SUSE_SLE-15-SP6_Update_images/81548244aad3728b4789d6b5ba7fa94d-sles15-image.SUSE_SLE-15-SP6_Update, com.suse.release-stage=released, org.opencontainers.image.ref.name=15.6.47.18.1, com.suse.manager.proxy-ssh.created=2025-04-11T10:33:24.457104122Z, com.suse.bci.base.description=Image for containers based on SUSE Linux Enterprise Server 15 SP6., com.suse.bci.base.name=15.6.47.18.1, org.opencontainers.image.url=https://www.suse.com/products/suse-manager, com.suse.bci.base.reference=registry.suse.com/bci/bci-base:15.6.47.18.1, org.opencontainers.image.created=2025-04-11T10:33:24.457104122Z, com.suse.supportlevel=l3, org.opencontainers.image.vendor=SUSE LLC, org.opencontainers.image.title=SUSE Manager proxy ssh container, org.opencontainers.image.name=proxy-ssh-image, com.suse.manager.proxy-ssh.eula=sle-eula, com.suse.bci.base.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, com.suse.manager.proxy-ssh.title=SUSE Manager proxy ssh container, com.suse.bci.base.url=https://www.suse.com/products/base-container-images/, org.opencontainers.image.description=Image contains a SUSE Manager proxy component to serve and forward ssh access, org.opencontainers.image.version=5.0.10, PODMAN_SYSTEMD_UNIT=uyuni-proxy-ssh.service, com.suse.manager.proxy-ssh.name=proxy-ssh-image, com.suse.bci.base.eula=sle-bci, com.suse.manager.proxy-ssh.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, com.suse.bci.base.vendor=SUSE LLC, com.suse.bci.base.version=15.6.47.18.1, com.suse.manager.proxy-ssh.release-stage=released, org.uyuni.version=5.0.4, org.opensuse.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14, org.openbuildservice.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, io.buildah.version=1.33.12, com.suse.manager.proxy-ssh.vendor=SUSE LLC, com.suse.bci.base.title=SLE BCI 15 SP6 Base, io.artifacthub.package.logo-url=https://opensource.suse.com/bci/SLE_BCI_logomark_green.svg, org.opencontainers.image.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, com.suse.bci.base.release-stage=released, com.suse.manager.proxy-ssh.description=Image contains a SUSE Manager proxy component to serve and forward ssh access, io.artifacthub.package.readme-url=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d//README.md, com.suse.manager.proxy-ssh.lifecycle-url=https://www.suse.com/lifecycle/, com.suse.manager.proxy-ssh.version=5.0.10, com.suse.manager.proxy-ssh.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14)
        Jun 02 11:38:00 mbsumapro502 sh[10276]: time="2025-06-02T11:38:00+02:00" level=warning msg="Path \"/etc/SUSEConnect\" from \"/etc/containers/mounts.conf\" doesn't exist, skipping"
        Jun 02 11:38:00 mbsumapro502 sh[10276]: time="2025-06-02T11:38:00+02:00" level=warning msg="Path \"/etc/zypp/credentials.d/SCCcredentials\" from \"/etc/containers/mounts.conf\" doesn't exist, skipping"
        Jun 02 11:38:00 mbsumapro502 podman[10276]: 2025-06-02 11:38:00.658191322 +0200 CEST m=+0.035338900 image pull d7153999b9090e4d5032f55cb8ea48c475cf0c0bd8440be425507c9278eb63fe localhost/suse/manager/5.0/x86_64/proxy-ssh:5.0.4
        Jun 02 11:38:00 mbsumapro502 podman[10276]: 2025-06-02 11:38:00.864499561 +0200 CEST m=+0.241647144 container init 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06 (image=localhost/suse/manager/5.0/x86_64/proxy-ssh:5.0.4, name=uyuni-proxy-ssh, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, com.suse.bci.base.created=2025-02-04T09:51:01.275197080Z, com.suse.release-stage=released, org.opencontainers.image.created=2025-04-11T10:33:24.457104122Z, com.suse.bci.base.vendor=SUSE LLC, io.buildah.version=1.33.12, com.suse.manager.proxy-ssh.description=Image contains a SUSE Manager proxy component to serve and forward ssh access, org.opencontainers.image.url=https://www.suse.com/products/suse-manager, com.suse.bci.base.disturl=obs://build.suse.de/SUSE:Maintenance:37326/SUSE_SLE-15-SP6_Update_images/81548244aad3728b4789d6b5ba7fa94d-sles15-image.SUSE_SLE-15-SP6_Update, PODMAN_SYSTEMD_UNIT=uyuni-proxy-ssh.service, com.suse.manager.proxy-ssh.vendor=SUSE LLC, com.suse.bci.base.title=SLE BCI 15 SP6 Base, com.suse.bci.base.release-stage=released, com.suse.bci.base.version=15.6.47.18.1, com.suse.manager.proxy-ssh.url=https://www.suse.com/products/suse-manager, com.suse.bci.base.name=15.6.47.18.1, com.suse.manager.proxy-ssh.created=2025-04-11T10:33:24.457104122Z, com.suse.bci.base.url=https://www.suse.com/products/base-container-images/, com.suse.manager.proxy-ssh.name=proxy-ssh-image, com.suse.supportlevel=l3, org.opencontainers.image.title=SUSE Manager proxy ssh container, org.uyuni.version=5.0.4, com.suse.bci.base.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, com.suse.lifecycle-url=https://www.suse.com/lifecycle/, com.suse.bci.base.description=Image for containers based on SUSE Linux Enterprise Server 15 SP6., com.suse.bci.base.authors=https://github.com/SUSE/bci/discussions, io.artifacthub.package.readme-url=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d//README.md, org.opencontainers.image.name=proxy-ssh-image, com.suse.manager.proxy-ssh.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14, com.suse.bci.base.lifecycle-url=https://www.suse.com/lifecycle#suse-linux-enterprise-server-15, com.suse.eula=sle-eula, org.openbuildservice.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, com.suse.manager.proxy-ssh.title=SUSE Manager proxy ssh container, com.suse.bci.base.supportlevel=l3, org.opencontainers.image.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, com.suse.manager.proxy-ssh.eula=sle-eula, com.suse.manager.proxy-ssh.lifecycle-url=https://www.suse.com/lifecycle/, org.opencontainers.image.version=5.0.10, org.opencontainers.image.ref.name=15.6.47.18.1, com.suse.manager.proxy-ssh.version=5.0.10, org.opensuse.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14, com.suse.bci.base.eula=sle-bci, org.opencontainers.image.authors=https://github.com/SUSE/bci/discussions, com.suse.manager.proxy-ssh.release-stage=released, com.suse.bci.base.reference=registry.suse.com/bci/bci-base:15.6.47.18.1, io.artifacthub.package.logo-url=https://opensource.suse.com/bci/SLE_BCI_logomark_green.svg, com.suse.manager.proxy-ssh.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, org.opencontainers.image.vendor=SUSE LLC, com.suse.manager.proxy-ssh.supportlevel=l3, org.opencontainers.image.description=Image contains a SUSE Manager proxy component to serve and forward ssh access)
        Jun 02 11:38:00 mbsumapro502 podman[10276]: 2025-06-02 11:38:00.871303402 +0200 CEST m=+0.248450965 container start 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06 (image=localhost/suse/manager/5.0/x86_64/proxy-ssh:5.0.4, name=uyuni-proxy-ssh, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, com.suse.manager.proxy-ssh.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14, com.suse.manager.proxy-ssh.supportlevel=l3, com.suse.manager.proxy-ssh.description=Image contains a SUSE Manager proxy component to serve and forward ssh access, org.opencontainers.image.version=5.0.10, com.suse.bci.base.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, com.suse.manager.proxy-ssh.release-stage=released, com.suse.manager.proxy-ssh.created=2025-04-11T10:33:24.457104122Z, com.suse.manager.proxy-ssh.vendor=SUSE LLC, com.suse.bci.base.description=Image for containers based on SUSE Linux Enterprise Server 15 SP6., org.opencontainers.image.url=https://www.suse.com/products/suse-manager, com.suse.release-stage=released, com.suse.supportlevel=l3, com.suse.bci.base.eula=sle-bci, com.suse.manager.proxy-ssh.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, org.opencontainers.image.vendor=SUSE LLC, org.opencontainers.image.authors=https://github.com/SUSE/bci/discussions, PODMAN_SYSTEMD_UNIT=uyuni-proxy-ssh.service, com.suse.manager.proxy-ssh.name=proxy-ssh-image, com.suse.eula=sle-eula, com.suse.bci.base.vendor=SUSE LLC, com.suse.bci.base.url=https://www.suse.com/products/base-container-images/, com.suse.lifecycle-url=https://www.suse.com/lifecycle/, com.suse.manager.proxy-ssh.eula=sle-eula, org.openbuildservice.disturl=obs://build.suse.de/SUSE:Maintenance:37875/SUSE_SLE-15-SP6_Update_Products_Manager50_Update_containerfile/774292f35f8dd5dd6ffd35aeffbd8326-proxy-ssh-image.SUSE_SLE-15-SP6_Update_Products_Manager50_Update, org.opencontainers.image.description=Image contains a SUSE Manager proxy component to serve and forward ssh access, com.suse.manager.proxy-ssh.url=https://www.suse.com/products/suse-manager, com.suse.bci.base.name=15.6.47.18.1, com.suse.bci.base.created=2025-02-04T09:51:01.275197080Z, org.opencontainers.image.ref.name=15.6.47.18.1, org.opencontainers.image.name=proxy-ssh-image, com.suse.bci.base.release-stage=released, com.suse.bci.base.disturl=obs://build.suse.de/SUSE:Maintenance:37326/SUSE_SLE-15-SP6_Update_images/81548244aad3728b4789d6b5ba7fa94d-sles15-image.SUSE_SLE-15-SP6_Update, com.suse.bci.base.reference=registry.suse.com/bci/bci-base:15.6.47.18.1, org.uyuni.version=5.0.4, org.opensuse.reference=registry.suse.com/suse/manager/5.0/x86_64/proxy-ssh:5.0.4.7.12.14, com.suse.manager.proxy-ssh.title=SUSE Manager proxy ssh container, com.suse.manager.proxy-ssh.lifecycle-url=https://www.suse.com/lifecycle/, com.suse.bci.base.version=15.6.47.18.1, io.artifacthub.package.logo-url=https://opensource.suse.com/bci/SLE_BCI_logomark_green.svg, com.suse.bci.base.authors=https://github.com/SUSE/bci/discussions, com.suse.bci.base.title=SLE BCI 15 SP6 Base, com.suse.bci.base.lifecycle-url=https://www.suse.com/lifecycle#suse-linux-enterprise-server-15, com.suse.bci.base.supportlevel=l3, org.opencontainers.image.source=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d/, io.buildah.version=1.33.12, io.artifacthub.package.readme-url=https://sources.suse.com/SUSE:Maintenance:37326/sles15-image.SUSE_SLE-15-SP6_Update/81548244aad3728b4789d6b5ba7fa94d//README.md, org.opencontainers.image.title=SUSE Manager proxy ssh container, org.opencontainers.image.created=2025-04-11T10:33:24.457104122Z, com.suse.manager.proxy-ssh.version=5.0.10)
        Jun 02 11:38:00 mbsumapro502 sh[10276]: 69ea5a1a1b54154c58e73e958f6b8254e6e4ad7f15fc6abd53b3abb404ebbf06
        Jun 02 11:38:00 mbsumapro502 systemd[1]: Started Uyuni proxy ssh container service.
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-ssh[10329]: Server listening on 0.0.0.0 port 22.
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-ssh[10329]: Server listening on :: port 22.
        * uyuni-proxy-tftpd.service - Uyuni proxy tftpd container service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-tftpd.service; disabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-tftpd.service.d
                     `-generated.conf
             Active: active (running) since Mon 2025-06-02 11:38:00 CEST; 1h 56min ago
            Process: 10272 ExecStartPre=/bin/rm -f /run/uyuni-proxy-tftpd.pid /run/uyuni-proxy-tftpd.ctr-id (code=exited, status=0/SUCCESS)
            Process: 10277 ExecStart=/bin/sh -c /usr/bin/podman run     --conmon-pidfile /run/uyuni-proxy-tftpd.pid     --cidfile /run/uyuni-proxy-tftpd.ctr-id         --cgroups=no-conmon          --pod-id-file /run/uyuni-proxy-pod.pod-id -d    --replace -dt   -v /etc/uyuni/proxy:/etc/uyuni:ro       -v uyuni-proxy-tftpboot:/srv/tftpboot:ro    --name uyuni-proxy-tftpd         ${UYUNI_IMAGE} (code=exited, status=0/SUCCESS)
           Main PID: 10351 (conmon)
              Tasks: 1
                CPU: 110ms
             CGroup: /system.slice/uyuni-proxy-tftpd.service
                     `-10351 /usr/bin/conmon --api-version 1 -c ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b -u ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b/userdata -p /run/containers/storage/overlay-containers/ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b/userdata/pidfile -n uyuni-proxy-tftpd --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b/userdata/oci-log -t --conmon-pidfile /run/uyuni-proxy-tftpd.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b

        Jun 02 11:38:00 mbsumapro502 sh[10277]: ae68573e376bf8d4f8bd38760ec20dc6df0e96c2cd377b488fbe41e63f5c528b
        Jun 02 11:38:00 mbsumapro502 systemd[1]: Started Uyuni proxy tftpd container service.
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:Starting TFTP proxy:
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:HTTP endpoint: localhost
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:Server FQDN: mbsuma50.mb.int
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:Proxy FQDN: mbsumapro502.mb.int
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:CA path: /usr/share/uyuni/ca.crt
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:Replace FQDNs: ['mbsuma50.mb.int']
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: INFO:root:SSL not used for inproxy communication
        Jun 02 11:38:01 mbsumapro502 uyuni-proxy-tftpd[10351]: WARNING:root:No callback specified for server statistics logging, will continue without
        * uyuni-proxy-pod.service - Podman uyuni-proxy-pod.service
             Loaded: loaded (/etc/systemd/system/uyuni-proxy-pod.service; enabled; preset: disabled)
            Drop-In: /etc/systemd/system/uyuni-proxy-pod.service.d
                     `-custom.conf
             Active: active (running) since Mon 2025-06-02 11:38:00 CEST; 1h 56min ago
            Process: 10124 ExecStartPre=/bin/rm -f /run/uyuni-proxy-pod.pid /run/uyuni-proxy-pod.pod-id (code=exited, status=0/SUCCESS)
            Process: 10126 ExecStartPre=/bin/sh -c /usr/bin/podman pod create --infra-conmon-pidfile /run/uyuni-proxy-pod.pid           --pod-id-file /run/uyuni-proxy-pod.pod-id --name uyuni-proxy-pod             --network uyuni          -p 8022:22          -p 4505:4505          -p 4506:4506          -p 443:443          -p 80:80          -p 69:69/udp                  --replace ${PODMAN_EXTRA_ARGS} (code=exited, status=0/SUCCESS)
            Process: 10136 ExecStart=/usr/bin/podman pod start --pod-id-file /run/uyuni-proxy-pod.pod-id (code=exited, status=0/SUCCESS)
           Main PID: 10242 (conmon)
              Tasks: 1
                CPU: 236ms
             CGroup: /system.slice/uyuni-proxy-pod.service
                     `-10242 /usr/bin/conmon --api-version 1 -c 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3 -u 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3 -r /usr/bin/runc -b /var/lib/containers/storage/overlay-containers/992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3/userdata -p /run/containers/storage/overlay-containers/992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3/userdata/pidfile -n 6145681f859b-infra --exit-dir /run/libpod/exits --full-attach -s -l journald --log-level warning --syslog --runtime-arg --log-format=json --runtime-arg --log --runtime-arg=/run/containers/storage/overlay-containers/992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3/userdata/oci-log --conmon-pidfile /run/uyuni-proxy-pod.pid --exit-command /usr/bin/podman --exit-command-arg --root --exit-command-arg /var/lib/containers/storage --exit-command-arg --runroot --exit-command-arg /run/containers/storage --exit-command-arg --log-level --exit-command-arg warning --exit-command-arg --cgroup-manager --exit-command-arg systemd --exit-command-arg --tmpdir --exit-command-arg /run/libpod --exit-command-arg --network-config-dir --exit-command-arg "" --exit-command-arg --network-backend --exit-command-arg netavark --exit-command-arg --volumepath --exit-command-arg /var/lib/containers/storage/volumes --exit-command-arg --db-backend --exit-command-arg sqlite --exit-command-arg --transient-store=false --exit-command-arg --runtime --exit-command-arg runc --exit-command-arg --storage-driver --exit-command-arg overlay --exit-command-arg --storage-opt --exit-command-arg overlay.mountopt=nodev,metacopy=on --exit-command-arg --events-backend --exit-command-arg journald --exit-command-arg container --exit-command-arg cleanup --exit-command-arg 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3

        Jun 02 11:38:00 mbsumapro502 podman[10126]: 2025-06-02 11:38:00.330253581 +0200 CEST m=+0.049746217 container create 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3 (image=localhost/podman-pause:4.9.5-1742299200, name=6145681f859b-infra, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, PODMAN_SYSTEMD_UNIT=uyuni-proxy-pod.service, io.buildah.version=1.33.12)
        Jun 02 11:38:00 mbsumapro502 podman[10126]: 2025-06-02 11:38:00.331625915 +0200 CEST m=+0.051118552 pod create 6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e (image=, name=uyuni-proxy-pod)
        Jun 02 11:38:00 mbsumapro502 sh[10126]: 6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e
        Jun 02 11:38:00 mbsumapro502 podman[10136]: time="2025-06-02T11:38:00+02:00" level=warning msg="Path \"/etc/SUSEConnect\" from \"/etc/containers/mounts.conf\" doesn't exist, skipping"
        Jun 02 11:38:00 mbsumapro502 podman[10136]: time="2025-06-02T11:38:00+02:00" level=warning msg="Path \"/etc/zypp/credentials.d/SCCcredentials\" from \"/etc/containers/mounts.conf\" doesn't exist, skipping"
        Jun 02 11:38:00 mbsumapro502 podman[10136]: 2025-06-02 11:38:00.579180591 +0200 CEST m=+0.210748817 container init 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3 (image=localhost/podman-pause:4.9.5-1742299200, name=6145681f859b-infra, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, PODMAN_SYSTEMD_UNIT=uyuni-proxy-pod.service, io.buildah.version=1.33.12)
        Jun 02 11:38:00 mbsumapro502 podman[10136]: 2025-06-02 11:38:00.584432939 +0200 CEST m=+0.216001154 container start 992e0b70979b0a195c78010d0a3ea3ff68db936de03a98abbf011817efaf51a3 (image=localhost/podman-pause:4.9.5-1742299200, name=6145681f859b-infra, pod_id=6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e, PODMAN_SYSTEMD_UNIT=uyuni-proxy-pod.service, io.buildah.version=1.33.12)
        Jun 02 11:38:00 mbsumapro502 podman[10136]: 2025-06-02 11:38:00.586805431 +0200 CEST m=+0.218373648 pod start 6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e (image=, name=uyuni-proxy-pod)
        Jun 02 11:38:00 mbsumapro502 podman[10136]: 6145681f859b4105d6337b2b05774e34297c94861ae0e5ee7325df0ab43c637e
        Jun 02 11:38:00 mbsumapro502 systemd[1]: Started Podman uyuni-proxy-pod.service.
    success:
        True
```

Stop the proxy on mbsumapro502:
```bash
uyuni-server:/srv/salt # salt 'mbsumapro502.mb.int' smlm_proxy.stop
mbsumapro502.mb.int:
    ----------
    message:
        1:37PM INF Welcome to mgrpxy
        1:37PM INF Executing command: stop
        1:37PM WRN Failed to find home directory error="$HOME is not defined"
    success:
        True
```
NOTE: the lines under message can be ignored.

Start the proxy on mbsumapro502:
```bash
uyuni-server:/srv/salt # salt 'mbsumapro502.mb.int' smlm_proxy.start
mbsumapro502.mb.int:
    ----------
    message:
        1:38PM INF Welcome to mgrpxy
        1:38PM INF Executing command: start
        1:38PM WRN Failed to find home directory error="$HOME is not defined"
    success:
        True

```
NOTE: the lines under message can be ignored.

Restart the proxy on mbsumapro502:
```bash
uyuni-server:/srv/salt # salt 'mbsumapro502.mb.int' smlm_proxy.restart
mbsumapro502.mb.int:
    ----------
    message:
        1:37PM INF Welcome to mgrpxy
        1:37PM INF Executing command: stop
        1:37PM WRN Failed to find home directory error="$HOME is not defined"
    success:
        True
```
NOTE: the lines under message can be ignored.

## State Modules

The following states are available:

**smlmproxy.stopped**
```yaml
proxy-stopped:
  smlmproxy.installed:
   - name: proxy
```

**smlmproxy.started**
```yaml
proxy-started:
  smlmproxy.installed:
   - name: proxy
```

**smlmproxy.restart**
```yaml
proxy-restart:
  smlmproxy.installed:
   - name: proxy
```

**smlmproxy.install**
```yaml
proxy-stopped:
  smlmproxy.installed:
   - name: proxy
   - internet_access: False
   - install_when_missing: True
   - cert_self_signed: False     # Self-signed certificates are not supported at this moment. Will follow later.
```








