FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN printf 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\n# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\n# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\n\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\n# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\n\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free\n# deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free' > /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -qqy less && \
    apt-get install -qqy vim && \
    apt-get install -qqy net-tools && \
    apt-get install -qqy procps && \
    apt-get install -qqy wget

RUN python3 -m pip install poetry -i "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/" && poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --no-dev