#!/usr/bin/env python3

from wsgiref.handlers import CGIHandler
from main import app

CGIHandler().run(app)
