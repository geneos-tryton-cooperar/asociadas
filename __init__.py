from trytond.pool import Pool
from .cuota import Cuota
from .cuotaprestamo import CuotaPrestamo, CreacionCuotasPrestamo, CreacionCuotasPrestamoStart
from .party import *

def register():
    Pool.register(
        Party,
        Cuota,
        CuotaPrestamo,
        CreacionCuotasPrestamoStart,
        module='asociadas', type_='model'
    )

    Pool.register(
        CreacionCuotasPrestamo,
        module='asociadas', type_='wizard')