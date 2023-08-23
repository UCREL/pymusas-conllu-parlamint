FROM ubuntu:jammy

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3
RUN apt-get install -y pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install https://github.com/UCREL/pymusas-models/releases/download/en_dual_none_contextual-0.3.3/en_dual_none_contextual-0.3.3-py3-none-any.whl
RUN python3 -m spacy download en_core_web_sm
RUN pip install conllu==4.4.2
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

CMD [ "python3", "./pymusas_conllu_parlamint.py" ]


