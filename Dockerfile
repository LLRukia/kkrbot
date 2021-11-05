FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN python3 -m pip install poetry -i "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/" && poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --no-dev