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


class Paciente:
    """Entidad de dominio con encapsulamiento estricto."""

    def __init__(self, dni: str, nombres: str, edad: int, caserio: str,
                 lengua_materna: str = "Quechua", tiene_sis: bool = True) -> None:
        self.dni = dni
        self.nombres = nombres
        self.edad = edad
        self.__caserio = caserio.strip()
        self.__lengua_materna = lengua_materna.strip()
        self.__tiene_sis = bool(tiene_sis)
        self.__historia = HistoriaClinica(f"HC-{hashlib.sha256(dni.encode()).hexdigest()[:6].upper()}")

    @property
    def dni_enmascarado(self) -> str:
        return f"DNI-****{self.__dni[-4:]}"

    @dni_enmascarado.setter
    def dni(self, valor: str) -> None:
        limpio = valor.strip()
        if not re.fullmatch(r"\d{8}", limpio):
            raise DatosInvalidosError("El DNI debe contener exactamente 8 dígitos numéricos.")
        self.__dni = limpio

    @property
    def nombres(self) -> str:
        return self.__nombres

    @nombres.setter
    def nombres(self, valor: str) -> None:
        if len(valor.strip()) < 3:
            raise DatosInvalidosError("El nombre del paciente es obligatorio.")
        self.__nombres = valor.strip()

    @property
    def edad(self) -> int:
        return self.__edad

    @edad.setter
    def edad(self, valor: int) -> None:
        if not (0 <= int(valor) <= 120):
            raise DatosInvalidosError("La edad debe estar entre 0 y 120 años.")
        self.__edad = int(valor)

    @property
    def lengua_materna(self) -> str:
        return self.__lengua_materna

    @property
    def historia(self) -> HistoriaClinica:
        return self.__historia


    def dni_hash(self) -> str:
        return hashlib.sha256(self.__dni.encode("utf-8")).hexdigest()[:12]

    def __str__(self) -> str:
        return f"{self.nombres} ({self.dni_enmascarado}) - {self.__caserio}"
