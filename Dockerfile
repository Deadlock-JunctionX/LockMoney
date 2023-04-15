FROM node:16-stretch AS frontend
LABEL maintainer="<lanpn lanpn@topcv.vn>"

RUN mkdir -p /app/frontend

COPY ./frontend/package.json /app/frontend/
COPY ./frontend/yarn.lock /app/frontend/

WORKDIR /app/frontend
RUN yarn

COPY ./frontend /app/frontend/
RUN yarn build

# ---

FROM python:3.10-slim as server

WORKDIR /app

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY --from=frontend /app/frontend/dist /dist

COPY . /app

CMD [ "./run-prod.sh" ]
