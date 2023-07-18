FROM python:3.10.10-slim

ENV HOME "/root"
ENV APP_HOME "$HOME/app"

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install poetry
ENV PATH "$HOME/.local/bin:$PATH"
RUN apt-get update && apt-get install --no-install-recommends -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt install python3-dev default-libmysqlclient-dev build-essential -y && \
    poetry config virtualenvs.create false && \
    apt-get install pkg-config -y

# install python packages
COPY pyproject.toml poetry.lock $APP_HOME
RUN poetry install --without=dev --no-root

# install app
COPY . $APP_HOME
RUN poetry install --only-root

EXPOSE 8000

# run app
WORKDIR $APP_HOME/assignment
CMD ["python", "manage.py", "runserver", "--settings=config.settings.production", "0.0.0.0:8000"]