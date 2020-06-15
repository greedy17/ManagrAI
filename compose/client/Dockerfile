FROM node:12-alpine

ARG NPM_PRIVATE_TOKEN

COPY ./client/.npmrc.example /app/client/.npmrc
COPY ./client/package.json /app/client/package.json

WORKDIR /app/client
RUN npm i

# start app
CMD ["npm", "run", "serve"]