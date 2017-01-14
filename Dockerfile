FROM python:2.7.13

RUN mkdir /aws_ir-api

ADD . /aws_ir-api

WORKDIR /aws_ir-api/api

RUN rm -rf bin/ include/ lib/ man/

RUN virtualenv . --clear

RUN . bin/activate

RUN pip install -r requirements.txt

WORKDIR /aws_ir-api/api/chalicelib

RUN rm -rf /aws_ir-api/api/chalicelib/aws_ir

RUN git clone https://github.com/ThreatResponse/aws_ir.git

WORKDIR /aws_ir-api/api/chalicelib/aws_ir

RUN git checkout development

RUN rm -rf bin/ include/ lib/ man/

RUN virtualenv .

RUN . bin/activate

RUN pip install -r requirements.txt

WORKDIR /aws_ir-api/api

CMD ['/aws_ir-api/bin/chalice', 'deploy']
