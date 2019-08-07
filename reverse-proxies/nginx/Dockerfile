FROM nginx:latest

LABEL IllumiDesk <contact@illumidesk.com>

RUN usermod -u 1000 nginx && \
    groupmod -g 1000 nginx

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
