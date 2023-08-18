ARG BASE_IMAGE=nvidia/opengl:1.2-glvnd-devel-ubuntu20.04
FROM ${BASE_IMAGE}

# Necessary to install tzdata. It will default to UTC.
ENV DEBIAN_FRONTEND=noninteractive

# Install apache2
RUN apt-get update && \
    apt-get install -y wget apache2 apache2-dev libapr1-dev apache2-utils gosu vim && \
    rm -rf /var/lib/apt/lists/*

# Set up needed permissions and users
# Create: /opt/viewer_server, /opt/viewer_server/launcher, /home/itech-user, /opt/viewer_server/proxy-mapping.txt, /deploy/server/www
RUN groupadd itech-user -g 1000 && \
    groupadd proxy-mapping -g 1001 && \
    useradd -u 1000 -g itech-user -G proxy-mapping -s /sbin/nologin itech-user && \
    usermod -a -G proxy-mapping www-data && \
    mkdir -p /opt/viewer_server && \
    chown -R itech-user:itech-user /opt/viewer_server && \
    mkdir -p /opt/viewer_server/launcher && \
    chown -R itech-user:itech-user /opt/viewer_server/launcher && \
    mkdir -p /home/itech-user && \
    chown -R itech-user:itech-user /home/itech-user && \
    touch /opt/viewer_server/proxy-mapping.txt && \
    chown itech-user:proxy-mapping /opt/viewer_server/proxy-mapping.txt && \
    chmod 660 /opt/viewer_server/proxy-mapping.txt && \
    mkdir -p /deploy/server/www && \
    chown -R itech-user:itech-user /deploy

# Set the apache configuration file
COPY config/apache2/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY config/apache2/ports.conf /etc/apache2/ports.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Configure the apache web server
RUN a2enmod vhost_alias && \
    a2enmod proxy && \
    a2enmod proxy_http && \
    a2enmod proxy_wstunnel && \
    a2enmod rewrite && \
    a2enmod headers && \
    a2dismod autoindex -f

# Install python3.11, python3.11-distutils, python-is-python3, python3.11-venv
RUN apt-get update && apt-get upgrade -y && \
    apt-get install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.11 python3.11-distutils python-is-python3 python3.11-venv && \
    rm -rf /var/lib/apt/lists/*

# Install libgl1, libxrender-dev
RUN apt-get update && \
    apt-get install -y libgl1 && \
    apt-get install -y libxrender-dev

# Set python3 to python3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Never use a cache directory for pip, both here in this Dockerfile and when we run the container.
ENV PIP_NO_CACHE_DIR=1

# Install and upgrade pip
RUN wget -q -O- https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    pip install -U pip

# Install dependencies
RUN pip install PyYAML \
    wheel \
    poetry \
    wslink \
    pydicom \
    python-dotenv \
    requests \
    numpy

# Update requests version
RUN pip install --upgrade requests

# Install vtk-egl
RUN pip install https://github.com/pyvista/pyvista-wheels/raw/main/vtk_egl-9.2.5-cp311-cp311-linux_x86_64.whl

# Set venv paths
ENV VIEWER_VENV=/deploy/server/venv
ENV PV_VENV=${VIEWER_VENV}
ENV VTK_VENV=${VIEWER_VENV}

# Copy the viewer project into place
COPY . /opt/viewer_server

WORKDIR /opt/viewer_server

EXPOSE 8000 8081 9000