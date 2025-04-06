#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o diretório atual ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    main() 