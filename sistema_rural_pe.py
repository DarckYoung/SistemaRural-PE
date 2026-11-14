"""Módulo funcional multiparadigma SistemaRural-PE (P.S. Intercultural CLAS Chetilla)."""

from abc import ABC, abstractmethod
from datetime import datetime
from functools import reduce
import hashlib
import re

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:
    tk = None
    messagebox = ttk = None


class DatosInvalidosError(ValueError):
    """Excepción lanzada cuando un dato clínico o identificador incumple invariantes."""


class CitaDuplicadaError(RuntimeError):
    """Excepción lanzada ante cruces de horario o registros repetidos."""
