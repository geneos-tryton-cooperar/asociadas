from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['Party']
__metaclass__ = PoolMeta

IVAS = [
        ('', ''),
        ('responsable_inscripto', 'Responsable Inscripto'),
        ('exento', 'Exento'),
        ('consumidor_final', 'Consumidor Final'),
        ('monotributo', 'Responsable Monotributo'),
        ('monotributo_promovido', 'Monotributo Trabajador Independiente Promovido'),
        ('monotributo_social', 'Monotributista Social'),
        ('no_alcanzado', 'No alcanzado'),
]
IVAS_DICT = dict(IVAS)

class Party:
    __name__ = 'party.party'

    asociada = fields.Boolean('Asociada', help="Marcar si es una asociada de la federacion")
    monto_actual_cuota = fields.Float('Monto Actual de la Cuota de Sostenimiento a pagar', states = {'required': Eval('asociada', True)})
    cuotas = fields.One2Many('asociadas.cuota', 'asociada', 'Cuotas')
    cuotaprestamos = fields.One2Many('asociadas.cuotaprestamo', 'asociada' ,'Cuotas de Prestamos')  

    iva_condition = fields.Selection(
            IVAS,
            'Condicion ante el IVA',
            states={
                'required' : Eval('asociada', True),
                'readonly' : ~Eval('active', True),
                },
            depends=['active'],
            )

    def get_iva_condition(self):
        return IVAS_DICT[self.iva_condition]
