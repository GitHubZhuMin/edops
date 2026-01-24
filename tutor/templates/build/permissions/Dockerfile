<<<<<<< HEAD
FROM docker.io/alpine:3.13.6
LABEL maintainer="Overhang.io <contact@overhang.io>"
=======
FROM zhjx-images.tencentcloudcr.com/library/alpine:3.13.6
LABEL maintainer="EdOps Team <im.zhumin@gmail.com>"
>>>>>>> origin/refactor/config-system-refactor

COPY ./setowner.sh /usr/local/bin/setowner
RUN chmod a+x /usr/local/bin/setowner

ENTRYPOINT ["setowner"]
