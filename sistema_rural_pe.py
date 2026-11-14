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


class EntradaClinica:
    """Entidad dependiente (composición fuerte) de HistoriaClinica."""

    def __init__(self, triaje: str, codigo_cie10: str, diagnostico: str) -> None:
        if not re.fullmatch(r"[A-Z]\d{2}(\.\d)?", codigo_cie10.strip().upper()):
            raise DatosInvalidosError("Código CIE-10 inválido (ej. J00 o O80.0).")
        self.__fecha = datetime.now()
        self.__triaje = triaje.strip()
        self.__codigo_cie10 = codigo_cie10.strip().upper()
        self.__diagnostico_hash = hashlib.sha256(diagnostico.encode("utf-8")).hexdigest()[:12]

    @property
    def codigo_cie10(self) -> str:
        return self.__codigo_cie10

    def resumen_anonimizado(self) -> dict[str, str]:
        return {
            "fecha": self.__fecha.strftime("%Y-%m-%d"),
            "cie10": self.__codigo_cie10,
            "dx_protegido": f"SHA256:{self.__diagnostico_hash}",
        }


class HistoriaClinica:
    """Historia clínica compuesta por entradas clínicas dependientes."""

    def __init__(self, numero_hc: str) -> None:
        self.__numero_hc = numero_hc
        self.__entradas: list[EntradaClinica] = []

    @property
    def numero_hc(self) -> str:
        return self.__numero_hc

    def agregar_entrada(self, entrada: EntradaClinica) -> None:
        self.__entradas.append(entrada)

    def obtener_entradas(self) -> tuple[EntradaClinica, ...]:
        return tuple(self.__entradas)


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


class PersonalSalud(ABC):
    """Superclase abstracta para polimorfismo de personal asistencial."""

    def __init__(self, codigo_colegiatura: str, nombre_completo: str) -> None:
        self._codigo_colegiatura = codigo_colegiatura
        self._nombre_completo = nombre_completo

    @property
    def nombre_completo(self) -> str:
        return self._nombre_completo

    @abstractmethod
    def calcular_duracion_cita(self) -> int:
        """Retorna duración estándar en minutos según especialidad."""


class Medico(PersonalSalud):
    def calcular_duracion_cita(self) -> int:
        return 20


class Enfermero(PersonalSalud):
    def calcular_duracion_cita(self) -> int:
        return 25


class Obstetra(PersonalSalud):
    def calcular_duracion_cita(self) -> int:
        return 30


class Cita:
    """Asocia un Paciente con un PersonalSalud y gestiona su estado."""

    def __init__(self, id_cita: str, paciente: Paciente, profesional: PersonalSalud,
                 fecha_hora: str, estado: str = "PENDIENTE") -> None:
        self.__id_cita = id_cita
        self.__paciente = paciente
        self.__profesional = profesional
        self.__fecha_hora = fecha_hora
        self.__estado = estado

    @property
    def paciente(self) -> Paciente:
        return self.__paciente

    @property
    def profesional(self) -> PersonalSalud:
        return self.__profesional

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def fecha_hora(self) -> str:
        return self.__fecha_hora

    def atender(self) -> None:
        self.__estado = "ATENDIDA"
