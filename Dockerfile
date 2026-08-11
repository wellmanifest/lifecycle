FROM python:3.12.11-alpine3.22@sha256:efcdfa6a6b2fd2afb9c7dfa9a5b288a6f68338b5cfdebe6b637d986067d85757

WORKDIR /workspace
COPY . /workspace

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspace/src

CMD ["sh", "-c", "if [ -d tests ]; then python3 -m unittest discover -s tests -v; else echo 'bootstrap: no tests yet'; fi"]
