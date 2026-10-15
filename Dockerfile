FROM nginx:alpine
RUN rm -f /etc/nginx/conf.d/default.conf
COPY app/ /usr/share/nginx/html/
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 10000
