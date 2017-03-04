FROM centos:6.7

RUN yum install -y https://s3.amazonaws.com/exchange-development-yum/exchange-development-repo-1.0.0.noarch.rpm
RUN yum update -y

RUN yum -y install boundless-vendor-libs \
                   libtiff-devel \
                   libxml2-devel \
                   libxslt-devel \
                   make \
                   gcc \
                   gcc-c++

RUN yum install -y python27 python27-devel python27-setuptools python27-virtualenv git
RUN /usr/local/bin/virtualenv /env && chmod -R 755 /env

EXPOSE 8001

RUN git clone https://github.com/boundlessgeo/registry/ /opt/registry/

ADD registry-settings.sh /etc/profile.d/


ADD setupdb.sh /root/
ADD run.sh /root/

# globally install what registry needs.
WORKDIR /opt/registry/
RUN source /env/bin/activate && pip install -r requirements.txt

# inititalize
RUN /root/setupdb.sh

CMD /root/run.sh
