#!/bin/bash

a = `curl -X GET -v -k https://127.0.0.1:8080/v1/pimJobs`
b = `curl -X DELETE -v -k https://127.0.0.1:8080/v1/pimJobs`
c = `curl -X POST -v -k https://127.0.0.1:8080/v1/pimJobs`
