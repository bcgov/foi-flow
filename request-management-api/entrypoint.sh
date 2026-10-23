#!/bin/bash
python manage.py db upgrade && exec python wsgi.py
