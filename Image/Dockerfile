FROM python:3.12.6-bookworm

RUN apt update
RUN apt install -y gcc
RUN apt install -y build-essential
RUN apt install -y default-jre-headless
RUN apt install -y openjdk-17-jdk-headless
RUN apt install -y mono-complete
RUN apt install -y sudo
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN pip3 install PyYAML

RUN groupadd -r user && useradd -r -g user -m -d /home/user user

COPY ./tester.py ./testEnv/
COPY ./java_compile.py ./testEnv/
COPY ./comparison_page_generator.py ./testEnv/
WORKDIR ./testEnv
CMD python3 ./tester.py
