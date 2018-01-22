# Previewer

Our link previewer! It returns JSON describing a given `url`. To use it, navigate to https://previews.ada.support/

We built this for ourselves, but you can use it too if you like.

## Requirements

This requires a running Redis instance.

You can spin one up easily with Docker

```
docker run -p 6379:6379 redis:3-alpine

```

## Getting Started

Build the docker image

```
docker build -t ada/preview .
```

Spin up a docker container

```
docker run -e REDIS_URL=redis://docker.for.mac.localhost:6379 -p 8000:8000 ada/preview:latest
```

For [Sentry](https://sentry.io/welcome/) configuration, add

```
-e SENTRY_DSN=$sentry_dsn

```

You can access the preview service at [http://localhost:8000](http://localhost:8000)

## Arguments

The only argument we need is a `url` pass it in as a url argument like this:

```sh
https://previews.ada.support/?url=slack.com
```

## Response

We return JSON with utf-8 characters encoded using `\u`. Here's what a good response might look like:

```js
{
    "desc": "Slack brings all your communication together in one place. It\u2019s real-time messaging, archiving and search for modern teams.",
    "title": "Slack: Where work happens",
    "icon": "https://a.slack-edge.com/66f9/img/icons/favicon-32.png"
}
```

## Errors
Errors will return a 400 status code and a `message` parameter describing the issue.
