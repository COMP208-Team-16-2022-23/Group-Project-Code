#!/usr/bin/env python3

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
