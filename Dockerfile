FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y tar gzip
COPY ./src/external/aws-nuke-v2.25.0-linux-amd64.tar.gz /tmp/aws-nuke.tar.gz
RUN tar -xzf /tmp/aws-nuke.tar.gz -C /opt/
RUN mv /opt/aws-nuke-v2.25.0-linux-amd64 /opt/aws-nuke
COPY ./src/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
COPY ./src ./

CMD [ "app.lambda_handler" ]