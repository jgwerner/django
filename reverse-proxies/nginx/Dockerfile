FROM ubuntu:16.04 AS build

LABEL IllumiDesk <contact@illumidesk.com>

# Install all OS dependencies for notebook server that starts but lacks all
# features (e.g., download as all possible file formats)
ENV DEBIAN_FRONTEND noninteractive
ENV NGINX_VERSION=1.14.2
ENV CC=gcc
ENV CFLAGS="-pipe -O2"

RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    wget \
	libpcre3-dev \
	zlib1g-dev \
    ca-certificates \
	build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /nginx
WORKDIR /tmp

RUN wget -qO- https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz | tar xz -C /tmp
RUN cd /tmp/nginx-${NGINX_VERSION} \
 && ./configure --prefix=/nginx \
	--without-select_module \
	--without-poll_module \
	--with-threads \
	--with-http_v2_module \
	--without-http_geo_module \
	--without-http_map_module \
	--without-http_proxy_module \
	--without-http_fastcgi_module \
	--without-http_scgi_module \
	--without-http_memcached_module \
	--without-http_upstream_hash_module \
	--without-http_upstream_ip_hash_module \
	--without-http_upstream_least_conn_module \
	--without-http_upstream_zone_module \
	--with-cc-opt="-static -static-libgcc" \
	--with-ld-opt="-static" \
 && make -j $(nproc) \
 && make install

FROM busybox:glibc

COPY --from=build nginx /nginx
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

WORKDIR /nginx
RUN touch logs/error.log
EXPOSE 80
EXPOSE 443
COPY nginx.conf /nginx/conf

CMD ["/nginx/sbin/nginx", "-g", "daemon off;"]
