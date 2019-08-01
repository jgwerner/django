FROM nginx:latest

LABEL IllumiDesk <contact@illumidesk.com>

RUN usermod -u 1000 nginx && \
    groupmod -g 1000 nginx

CMD ["nginx", "-g", "daemon off;"]