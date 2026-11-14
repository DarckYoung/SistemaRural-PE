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


class GestorAuditoria:
    """Patrón Singleton: centraliza la bitácora de auditoría sin texto plano."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.__bitacora = []
        return cls._instancia

    @classmethod
    def obtener_instancia(cls) -> "GestorAuditoria":
        return cls()

    def registrar_evento(self, accion: str, dni_hash: str) -> None:
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__bitacora.append(f"[{marca}] {accion} | REF:{dni_hash}")

    def obtener_bitacora(self) -> tuple[str, ...]:
        return tuple(self.__bitacora)


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


def procesar_atenciones_funcional(citas: tuple[Cita, ...], solo_quechua: bool = False) -> dict[str, object]:
    """Pipeline funcional puro (filter -> map -> reduce) sin mutar la colección."""
    atendidas = tuple(filter(
        lambda c: c.estado == "ATENDIDA" and (not solo_quechua or c.paciente.lengua_materna.lower() == "quechua"),
        citas,
    ))
    resumenes = tuple(map(
        lambda c: (c.paciente.dni_enmascarado, c.profesional.nombre_completo, c.profesional.calcular_duracion_cita()),
        atendidas,
    ))
    total_minutos = reduce(lambda acc, item: acc + item[2], resumenes, 0)
    return {
        "total_atenciones": len(resumenes),
        "total_minutos": total_minutos,
        "registros_seguros": resumenes,
    }


class ReporteClinico(ABC):
    """Producto abstracto del patrón Factory Method."""

    @abstractmethod
    def generar(self, citas: tuple[Cita, ...]) -> dict[str, object]:
        """Genera un resumen estadístico sin exponer datos sensibles."""


class ReporteHIS(ReporteClinico):
    def generar(self, citas: tuple[Cita, ...]) -> dict[str, object]:
        return procesar_atenciones_funcional(citas, solo_quechua=False)


class ReporteMorbilidad(ReporteClinico):
    def generar(self, citas: tuple[Cita, ...]) -> dict[str, object]:
        return procesar_atenciones_funcional(citas, solo_quechua=True)


class ReporteFactory:
    """Patrón Factory Method: desacopla la creación de reportes DIRESA."""

    @staticmethod
    def crear_reporte(tipo: str) -> ReporteClinico:
        tipos = {"HIS": ReporteHIS, "MORBILIDAD": ReporteMorbilidad}
        clave = tipo.strip().upper()
        if clave not in tipos:
            raise DatosInvalidosError(f"Tipo de reporte no soportado: {tipo}")
        return tipos[clave]()


class ControladorClinico:
    """Controlador desacoplado (SRP) que coordina dominio, auditoría y reportes."""

    def __init__(self) -> None:
        self.__pacientes: dict[str, Paciente] = {}
        self.__citas: list[Cita] = []
        self.__auditoria = GestorAuditoria.obtener_instancia()

    def registrar_paciente_y_cita(self, dni: str, nombres: str, edad: int, caserio: str,
                                  lengua: str, profesional: PersonalSalud, fecha_hora: str) -> Cita:
        paciente = Paciente(dni=dni, nombres=nombres, edad=edad, caserio=caserio, lengua_materna=lengua)
        clave_hash = paciente.dni_hash()
        if clave_hash in self.__pacientes:
            raise CitaDuplicadaError(f"El paciente {paciente.dni_enmascarado} ya está registrado.")
        for cita in self.__citas:
            if cita.profesional is profesional and cita.fecha_hora == fecha_hora:
                raise CitaDuplicadaError("El profesional ya tiene una cita en ese horario.")
        self.__pacientes[clave_hash] = paciente
        nueva_cita = Cita(f"CIT-{len(self.__citas) + 1:03d}", paciente, profesional, fecha_hora)
        self.__citas.append(nueva_cita)
        self.__auditoria.registrar_evento("REGISTRO_CITA", clave_hash)
        return nueva_cita

    def obtener_citas_inmutables(self) -> tuple[Cita, ...]:
        return tuple(self.__citas)


class VentanaSistemaRural:
    """Capa de presentación orientada a eventos con tkinter."""

    def __init__(self, root) -> None:
        self.root = root
        self.root.title("SistemaRural-PE · P.S. CLAS Chetilla")
        self.controlador = ControladorClinico()
        self.medico = Medico("CMP-097341", "Dr. Luis Huamán")
        self._construir_interfaz()

    def _construir_interfaz(self) -> None:
        marco = ttk.Frame(self.root, padding=12)
        marco.pack(fill="both", expand=True)
        self.ent_dni = ttk.Entry(marco)
        self.ent_nom = ttk.Entry(marco)
        self.ent_edad = ttk.Entry(marco)
        for etiqueta, widget in [("DNI (8 dígitos):", self.ent_dni), ("Nombres:", self.ent_nom), ("Edad:", self.ent_edad)]:
            ttk.Label(marco, text=etiqueta).pack(anchor="w")
            widget.pack(fill="x", pady=2)
        self.btn_guardar = ttk.Button(marco, text="Registrar Cita", command=self._al_registrar_cita)
        self.btn_guardar.pack(pady=8)
        self.lista = tk.Listbox(marco, width=55, height=6)
        self.lista.pack(fill="both", expand=True)

    def _al_registrar_cita(self) -> None:
        self.btn_guardar.config(state="disabled")
        try:
            cita = self.controlador.registrar_paciente_y_cita(
                self.ent_dni.get(), self.ent_nom.get(), int(self.ent_edad.get()),
                "Chetilla", "Quechua", self.medico, "2026-11-13 09:00",
            )
            self.lista.insert(tk.END, f"{cita.paciente} | {cita.profesional.calcular_duracion_cita()} min")
        except (DatosInvalidosError, CitaDuplicadaError, ValueError) as err:
            messagebox.showerror("Validación Clínica", str(err))
        finally:
            self.btn_guardar.config(state="normal")


if __name__ == "__main__":
    raiz = tk.Tk()
    app = VentanaSistemaRural(raiz)
    raiz.mainloop()
