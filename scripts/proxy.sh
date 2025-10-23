PROXY_HOST=192.168.1.13
PROXY_PORT=7890

export https_proxy=http://$PROXY_HOST:$PROXY_PORT http_proxy=http://$PROXY_HOST:$PROXY_PORT all_proxy=socks5://$PROXY_HOST:$PROXY_PORT
export no_proxy=localhost,127.0.0.1,.local,.internal
