FROM python:3.10-slim

ENV POETRY_HOME=/poetry
ENV PATH=${PATH}:/root/.local/bin
RUN pip install poetry

RUN useradd -ms /bin/bash hydroplane
USER hydroplane
WORKDIR /home/hydroplane/

COPY poetry.lock pyproject.toml /home/hydroplane/

RUN poetry config virtualenvs.create false
RUN poetry export --format requirements.txt -o requirements.txt
RUN pip install --user -r requirements.txt

COPY hydroplane/ /home/hydroplane/hydroplane/
COPY bin/ /home/hydroplane/bin/

ENV PATH="${PATH}:/home/hydroplane/.local/bin"

ENTRYPOINT ["/home/hydroplane/bin/hydroplane"]
