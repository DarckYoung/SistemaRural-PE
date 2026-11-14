"""Suite de pruebas automatizadas (TDD / unittest y pytest) para SistemaRural-PE."""

import unittest
from sistema_rural_pe import (
    Cita, CitaDuplicadaError, ControladorClinico, DatosInvalidosError,
    Enfermero, EntradaClinica, GestorAuditoria, Medico, Obstetra,
    Paciente, ReporteFactory,
)


class TestSistemaRural(unittest.TestCase):
    def test_encapsulamiento_y_proteccion_ley_29733(self):
        paciente = Paciente("71458923", "Rosa Quispe", 34, "Cochapampa", "Quechua")
        self.assertEqual(paciente.dni_enmascarado, "DNI-****8923")
        self.assertNotIn("71458923", str(paciente))
        with self.assertRaises(DatosInvalidosError):
            Paciente("123", "Juan", 25, "Chetilla")

    def test_polimorfismo_personal_y_composicion_historia(self):
        self.assertEqual(Medico("CMP-1", "Dr. A").calcular_duracion_cita(), 20)
        self.assertEqual(Enfermero("CEP-2", "Lic. B").calcular_duracion_cita(), 25)
        self.assertEqual(Obstetra("COP-3", "Obs. C").calcular_duracion_cita(), 30)
        paciente = Paciente("42891034", "María Chilón", 28, "Jamcate")
        entrada = EntradaClinica("PA 110/70", "O80.0", "Control prenatal normal")
        paciente.historia.agregar_entrada(entrada)
        self.assertEqual(len(paciente.historia.obtener_entradas()), 1)
        self.assertNotIn("Control prenatal", str(entrada.resumen_anonimizado()))

    def test_singleton_factory_y_pipeline_funcional_inmutable(self):
        self.assertIs(GestorAuditoria.obtener_instancia(), GestorAuditoria.obtener_instancia())
        p1 = Paciente("75120984", "Lucía Mantilla", 40, "Manzano", "Quechua")
        p2 = Paciente("41029384", "Carlos Pérez", 52, "Chetilla", "Castellano")
        c1 = Cita("C1", p1, Obstetra("COP-3", "Obs. C"), "2026-11-13 08:00")
        c2 = Cita("C2", p2, Medico("CMP-1", "Dr. A"), "2026-11-13 08:30")
        c1.atender()
        c2.atender()
        lote = (c1, c2)
        reporte = ReporteFactory.crear_reporte("MORBILIDAD").generar(lote)
        self.assertEqual(reporte["total_atenciones"], 1)
        self.assertEqual(reporte["total_minutos"], 30)
        self.assertEqual(len(lote), 2)

    def test_controlador_impide_duplicidad_dni(self):
        ctrl = ControladorClinico()
        med = Medico("CMP-097341", "Dr. Huamán")
        ctrl.registrar_paciente_y_cita("70998877", "Ana Rojas", 29, "Paltapampa", "Quechua", med, "09:00")
        with self.assertRaises(CitaDuplicadaError):
            ctrl.registrar_paciente_y_cita("70998877", "Ana Rojas", 29, "Paltapampa", "Quechua", med, "09:30")


if __name__ == "__main__":
    unittest.main(verbosity=2)
