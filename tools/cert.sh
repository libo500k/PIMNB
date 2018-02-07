#!/bin/bash
#Generate a self-signed certificate compounded of a certificate and a private key for your server with the following command 
#(it outputs them both in a single file named server.pem): 

a=`penssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes`


