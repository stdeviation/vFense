import ConfigParser
import os

from vFense.utils.common import get_nginx_config_location
from vFense._constants import (
    VFENSE_WWW_PATH, VFENSE_APP_PATH, VFENSE_CONFIG,
    VFENSE_APP_TMP_PATH, VFENSE_SSL_PATH
)

NGINX_CONFIG_FILE = get_nginx_config_location()
base_nginx_config = """server {
    listen         80;
    server_name    %(server_name)s localhost _;
    rewrite        ^ https://$server_name$request_uri? permanent;
}

server {
    listen                      443;
    server_name                 _;
    ssl                         on;
    ssl_certificate             %(ssl_crt)s;
    ssl_certificate_key         %(ssl_key)s;

    ssl_session_timeout         5m;

    ssl_protocols               SSLv3 TLSv1;
    ssl_ciphers                 ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv3:+EXP;
    ssl_prefer_server_ciphers   on;
    client_max_body_size        1G;
    client_body_buffer_size     100m;

    location /nginx_status {
        stub_status on;
        access_log   off;
        allow 192.168.0.0/16;
        allow 127.0.0.1;
        deny all;
    }

    location ^~ /api/v1/apps/upload {
        auth_request                /api/v1/authenticated;
        client_body_temp_path       /tmp/apps/;

        client_body_in_file_only    on;
        client_body_buffer_size     128K;
        proxy_set_header            X-FILE $request_body_file;
        proxy_pass_request_headers  on;
        proxy_set_header            Content-Length "";
        proxy_set_body              off;
        proxy_redirect              off;
        proxy_pass_request_body     off;
        proxy_pass                  https://vfweb;
    }

    location ^~ /api/v1/authenticated {
        proxy_pass_request_body     off;
        proxy_set_header            Content-Length "";
        proxy_set_header            Content-Type "";
        proxy_set_header            X-Original-URI $request_uri;
        proxy_pass                  https://vfweb;
    }

    location ^~ /api/ {
        proxy_pass              https://vfweb;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_intercept_errors  off;
        proxy_redirect          http:// https://;
    }

    location ~ /ra/websockify/(.*)/([0-9]+) {
        proxy_pass              http://$1:$2/websockify;
        proxy_read_timeout      2592000;
        proxy_http_version      1.1;
        proxy_set_header        Upgrade $http_upgrade;
        proxy_set_header        Connection "upgrade";
    }

    location ~ /ra/(.*)/([0-9]+)/(.*$) {
        proxy_pass              http://$1:$2/$3;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_intercept_errors  off;
        proxy_redirect          http:// https://;
    }

    location  ^~ /ws/ {
        proxy_pass              https://vfweb;
        proxy_read_timeout      604800; # 7 days
        proxy_http_version      1.1;
        proxy_set_header        Upgrade $http_upgrade;
        proxy_set_header        Connection "upgrade";
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        #proxy_send_timeout      300;
    }

    location ^~ /rvl/ {
        proxy_pass              https://vflistener;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_intercept_errors  off;
        proxy_redirect          http:// https://;
    }

    location ~* \.(?:ico|css|js|gif|jpe?g|png)$ {
        root                    %(www_path)s;
        expires                 max;
        add_header              Pragma public;
        add_header              Cache-Control "public, must-revalidate, proxy-revalidate";
    }

    location ~ %(app_path)s {
        root                    %(app_path)s;
        expires                 max;
        add_header              Pragma public;
        add_header              Cache-Control "public, must-revalidate, proxy-revalidate";
    }

    location  ^~ /# {
        proxy_pass              https://vfweb;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect          http:// https://;
    }

    location  / {
        proxy_pass              https://vfweb;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect          http:// https://;
    }

}"""

def nginx_config_builder(server_name='127.0.0.1'):

    Config = ConfigParser.ConfigParser()
    Config.read(VFENSE_CONFIG)

    ssl_key = Config.get('Listener', 'ssl_key')
    if not ssl_key:
        ssl_key = os.path.join(VFENSE_SSL_PATH, 'server.key')
        Config.set('Listener', 'ssl_key', ssl_key)

    ssl_cert = Config.get('Listener', 'ssl_cert')
    if not ssl_cert:
        ssl_cert = os.path.join(VFENSE_SSL_PATH, 'server.crt')
        Config.set('Listener', 'ssl_cert', ssl_cert)

    config_file = open(VFENSE_CONFIG, 'w')
    Config.write(config_file)
    config_file.close()

    vflistener_ending_port = int(Config.get('Listener', 'ending_port'))
    vflistener_starting_port = int(Config.get('Listener', 'starting_port'))

    vfweb_ending_port = int(Config.get('Api', 'ending_port'))
    vfweb_starting_port = int(Config.get('Api', 'starting_port'))

    vflistener_count = vflistener_ending_port - vflistener_starting_port
    vflistener_port = vflistener_starting_port
    vflistener_config = 'upstream vflistener {\n'

    for i in range(vflistener_count):
        vflistener_config += '    server 127.0.0.1:%s;\n' % (vflistener_port)
        vflistener_port += 1

    vflistener_config += '}\n\n'

    vfweb_count = vfweb_ending_port - vfweb_starting_port
    vfweb_port = vfweb_starting_port
    vfweb_config = 'upstream vfweb {\n'
    for i in range(vfweb_count):
        vfweb_config += '    server 127.0.0.1:%s;\n' % (vfweb_port)
        vfweb_port += 1

    vfweb_config += '}\n\n'
    replace_config = (
        base_nginx_config %
        {
            'server_name': server_name,
            'ssl_crt': ssl_cert,
            'ssl_key': ssl_key,
            'app_path': VFENSE_APP_PATH,
            'app_tmp_path': VFENSE_APP_TMP_PATH,
            'www_path': VFENSE_WWW_PATH,
        }
    )
    new_config = vflistener_config + vfweb_config + replace_config
    CONFIG_FILE = open(NGINX_CONFIG_FILE, 'w', 0)
    CONFIG_FILE.write(new_config)
    CONFIG_FILE.close()
