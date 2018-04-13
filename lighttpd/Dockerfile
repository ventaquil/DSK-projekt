FROM alpine

RUN apk update && \
      apk add lighttpd

EXPOSE 80

ENTRYPOINT lighttpd -f /etc/lighttpd/lighttpd.conf && tail -Fqn0 /var/log/lighttpd/*.log

