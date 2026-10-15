FROM python:3.12-alpine
WORKDIR /app
RUN mkdir -p /data
COPY api/server.py /app/server.py
COPY automation/ticketing/tickets.json /data/tickets.json
COPY docs/ /docs/
COPY runbooks/ /runbooks/
COPY postmortems/ /postmortems/
COPY automation/failures/evidence/ /evidence/
EXPOSE 10000
CMD ["python", "-u", "/app/server.py"]
