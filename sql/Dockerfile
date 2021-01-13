FROM postgres:12

# set authentication free access
ENV POSTGRES_HOST_AUTH_METHOD trust

# add example raw csv data
ADD data/*.gz /

# add sql scripts to initialization scripts
ADD sql/*.gz /docker-entrypoint-initdb.d/