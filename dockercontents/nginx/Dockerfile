FROM nginx


RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./slackpro.conf /etc/nginx/conf.d/
COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx","-g","daemon off;"]
