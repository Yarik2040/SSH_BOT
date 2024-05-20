FROM postgres:latest
COPY init.s* /docker-entrypoint-initdb.d/

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=Qq12345
ENV POSTGRES_DB=db_bot

RUN chmod +x /docker-entrypoint-initdb.d/init.sh