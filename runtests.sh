#! /bin/bash

export AWS_DEFAULT_REGION=us-east-1

pytest --flakes lambdapool
pytest --cov=lambdapool tests "$@"
