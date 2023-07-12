FROM ubuntu/apache2

RUN echo "Installing packages ..." && a2enmod vhost_alias && \
    a2enmod proxy && \
    a2enmod proxy_http && \
    a2enmod proxy_wstunnel && \
    a2enmod rewrite && \
    a2enmod headers && \
    a2dismod autoindex -f

CMD ["service", "apache2", "stop"]
CMD ["apache2ctl", "-D", "FOREGROUND"]