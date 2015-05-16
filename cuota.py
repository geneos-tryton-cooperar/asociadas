from trytond.model import ModelSQL, ModelView, fields

__all__ = ['Cuota', 'ReciboCuotaReport']

class Cuota(ModelSQL, ModelView):
    "Cuota"
    __name__ = 'asociadas.cuota'

    mes = fields.Selection(
        [
            ('1', '01'),
            ('2', '02'),
            ('3', '03'),
            ('4', '04'),
            ('5', '05'),
            ('6', '06'),
            ('7', '07'),
            ('8', '08'),
            ('9', '09'),
            ('10', '10'),
            ('11', '11'),
            ('12', '12'),
        ],
        'Mes', required=True
    )
    anio = fields.Integer('Anio', required=True)
    monto = fields.Float('Monto', (10,2), required=True)
    pagada = fields.Boolean('Pagada')
    fecha_pago = fields.Date('Fecha de Pago')
    asociada = fields.Many2One('party.party', 'Asociada', required=True, domain=[('asociada', '=', True)])  

    def get_mes_anio_proxima_cuota(self, asociada):
        #REVISAR ESTA PARTE
        #import pudb;pu.db
        ultima_cuota = self.search([('asociada', '=', asociada)], order=[('mes', 'ASC'), ('anio', 'ASC'),])
        if ultima_cuota:
            if ultima_cuota[0].mes == 12:
                mes_proxima_cuota = 1
                anio_proxima_cuota = int(ultima_cuota[0].anio) + 1
            else:
                mes_proxima_cuota = int(ultima_cuota[0].mes) + 1
                anio_proxima_cuota = ultima_cuota[0].anio
        else:
            #Dar de alta la ultima cuota REAL, sino 01/2015
            mes_proxima_cuota = 1
            anio_proxima_cuota = 2015

        return str(mes_proxima_cuota) + '-' + str(anio_proxima_cuota)

