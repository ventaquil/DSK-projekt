FROM alpine

RUN apk update && \
      apk add lighttpd openrc php7-common php7-cgi fcgi

RUN rc-update add lighttpd default

RUN sed -i '/tty/d' /etc/inittab && \
		sed -i 's/#rc_sys=""/rc_sys="docker"/g' /etc/rc.conf && \
		echo 'rc_provide="loopback net"' >> /etc/rc.conf && \
		sed -i 's/^#\(rc_logger="YES"\)$/\1/' /etc/rc.conf && \
		sed -i 's/hostname $opts/# hostname $opts/g' /etc/init.d/hostname && \
		sed -i 's/mount -t tmpfs/# mount -t tmpfs/g' /lib/rc/sh/init.sh && \
		sed -i 's/cgroup_add_service /# cgroup_add_service /g' /lib/rc/sh/openrc-run.sh && \
		rm -f hwclock hwdrivers modules modules-load modloop

RUN mkdir -p /var/lib/lighttpd/cache/compress

EXPOSE 80

CMD ["/sbin/init"]

