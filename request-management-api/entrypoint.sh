#!/bin/bash


python manage.py db upgrade && python wsgi.py