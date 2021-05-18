## Deny access to any other host
#server {
#    listen 80;
#    server_name _ default;
#    return 444;
#}

events {
    worker_connections  1024;
}

http {
    include /etc/nginx/sites-enabled/*;

    # The Django Application
    upstream managr-django {
        server 127.0.0.1:8000;
    }

    upstream managr-websockets {
        server 127.0.0.1:8001;
    }

    server {
        listen   80 default_server;
        server_name ${dns_name};
        ssi      on;

        # Set up HTTP Strict Transport Security (HSTS) with a 1-day lifespan
        # add_header Strict-Transport-Security "max-age=17280000; includeSubdomains";

        location /health-check {
            access_log off;
            return 200 "healthy\n";
        }

        location ~ ^/.well-known/microsoft-identity-association.json {
            root /var/www/html/;
        }

        # Redirect insecure traffic to https. The load balancer will
        # set the X-Forwarded-Proto header to let us know if the incoming
        # request was secure or insecure.
        # if ($http_x_forwarded_proto != "https") {
        #     return 302 ${app_url}$request_uri;
        # }

        # This is NECESSARY to make sure application redirects
        # point to https and not http
        # proxy_set_header X-Forwarded-Proto https;

        # gzip settings
        gzip on;
        gzip_comp_level 6;
        gzip_disable "msie6";
        gzip_min_length 200;
        #
        proxy_pass_header Server;
        proxy_set_header Nginx-SSI on;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 20s;
        proxy_read_timeout 20s;
        proxy_redirect off;
        proxy_intercept_errors on;
        #
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;
        #
        client_max_body_size 20m;

        ## TODO Deny illegal Host headers
        #if ($host !~* ^(app.managr.ai)$ ) {
        #    return 444;
        #}

        # TODO maintenance screen location
        #location / {
        #    alias /opt/managr/server/templates/503.html;
        #}

        location /zoomverify/verifyzoom.html {
            return 200 "7622e645b6eb4d0f877d22bf9ea97b91";
        }

        location /ws/ {
            try_files $uri @proxy_to_ws;
        }

        location @proxy_to_ws {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_redirect off;

            proxy_pass http://managr-websockets;
        }

        # location /static/ {
        #     alias /opt/managr/server/static/;
        #     access_log off;
        #     log_not_found on;
        #     expires 30d;
        #     add_header Pragma public;
        #     add_header Cache-Control "public";
        # }

        # TODO: Probably not necessary, since media files are on S3
        #location /media/ {
        #    alias /opt/managr/server/mediafiles/;
        #    access_log off;
        #    log_not_found on;
        #}

        # TODO: Add robots.txt
        #location /robots.txt {
        #    alias /opt/managr/...;
        #    log_not_found on;
        #}

        location /api/ {
            # prevent the browser from caching api responses
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate";
            proxy_pass http://managr-django;
            error_page 404 502 413 = @cache_miss;
        }

        rewrite ^/(admin)$ http://$http_host/$1/ permanent;

        location ^~ /admin/ {
            proxy_pass http://managr-django;
            allow  all;
            deny   all;
        }

        location = /favicon.ico { access_log off; log_not_found on; }

        location ~ /\.          { access_log off; log_not_found off; deny all; }

        location / {
            # Uncomment the lines below to activate 'maintenance mode'
            # Redirect everyone except the IP below to a 503 error
            ##if ($remote_addr != "107.206.176.194") {
            ##    return 503;
            ##}

            # Pass proxy and report user's IP address to Django
            proxy_pass http://managr-django;
            proxy_set_header    Host $host;
            proxy_set_header    X-Real-IP $remote_addr;
            proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;

            error_page 404 502 413 = @cache_miss;
            error_page 503 /503.html;
        }

        location @cache_miss {
            proxy_pass http://managr-django;
        }

        # what to serve if upstream is not available or crashes
        error_page 500 502 503 504 /50x;
    }

    server {
        listen 81;
        server_name localhost;

        access_log off;

        location /nginx_status {
            stub_status;

            server_tokens on;
        }
    }
}
