from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval, And, Bool, Equal, Not, Or
from trytond.pool import Pool
from datetime import datetime, timedelta, date
from trytond.transaction import Transaction
from decimal import Decimal

class CuotaPrestamo(ModelSQL, ModelView):
    "Cuota Prestamo"
    __name__ = 'asociadas.cuotaprestamo'

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
    porcentaje_interes = fields.Float('Porcentaje Interes', (10,2), required=True)
    interes = fields.Float('Monto Interes', (10,2), required=True)
    pagada = fields.Boolean('Pagada')
    fecha_vencimiento = fields.Date('Fecha de Vencimiento')
    fecha_pago = fields.Date('Fecha de Pago')
    asociada = fields.Many2One('party.party', 'Asociada', required=True, readonly=True, domain=[('asociada', '=', True)])  
    #datos generales del prestamo, a falta de cabecera
    monto_total_prestamo = fields.Float('Monto del Prestamo', (10,2) , required=True, readonly=True)
    cantidad_cuotas =  fields.Integer('Cantidad de cuotas', required=True, readonly=True)
    mes_primera_cuota = fields.Integer('Mes de la primera cuota', required=True, readonly=True)
    anio_primera_cuota = fields.Integer('Anio de la primera cuota', required=True, readonly=True)
    #Cuentas Contables
    cuenta_debito = fields.Many2One('account.account', 'Cuenta Debito', required=True, readonly=True)
        #domain=[('kind', '=', 'receivable')])
    cuenta_credito = fields.Many2One('account.account', 'Cuenta Credito', required=True, readonly=True)
        #domain=[('kind', '=', 'payable')])
    fecha_creacion = fields.Date('Fecha de Creacion', readonly = True)

#----------------------------Wizard de creacion----------------------------------#

class CreacionCuotasPrestamoStart(ModelView):
    "Creacion de Cuotas de un Prestamo"
    __name__= 'asociadas.creacion_cuotas_prestamo.start'

    monto_prestamo = fields.Float('Monto del Prestamo', (10,2) , required=True)
    asociada = fields.Many2One('party.party', 'Asociada', required=True, domain=[('asociada', '=', True)])  
    cantidad_cuotas = fields.Integer('Cantidad de cuotas', required=True)
    interes_mensual = fields.Float('Interes Mensual %', (10,2) , required=True)
    dia_vencimiento = fields.Integer('Dia del mes que vence', required=True)
    mes_primera_cuota = fields.Integer('Mes de la primera cuota', required=True)
    anio_primera_cuota = fields.Integer('Anio de la primera cuota', required=True)
    #Cuentas Contables
    cuenta_debito = fields.Many2One('account.account', 'Cuenta Debito', required=True)
        #domain=[('kind', '=', 'receivable')])
    cuenta_credito = fields.Many2One('account.account', 'Cuenta Credito', required=True)
        #domain=[('kind', '=', 'payable')])


class CreacionCuotasPrestamo(Wizard):
    "Creacion de Cuotas de un Prestamo"
    __name__= 'asociadas.creacion_cuotas_prestamo'

    start = StateView('asociadas.creacion_cuotas_prestamo.start', 'asociadas.view_creacion_form',
                      [Button('Cancelar', 'end', 'tryton-cancel'),
                       Button('Crear Prestamo', 'crear', 'tryton-go-next', default = True)])

    crear = StateTransition()

    
    def transition_crear(self):
        valor_cuota_sin_interes = round(self.start.monto_prestamo / self.start.cantidad_cuotas,2)
        monto_interes_mensual = round((valor_cuota_sin_interes*self.start.interes_mensual)/100,2)
        valor_cuota_con_interes = valor_cuota_sin_interes + monto_interes_mensual

        CuotaPrestamo = Pool().get('asociadas.cuotaprestamo')
        mes_actual = self.start.mes_primera_cuota
        anio_actual = self.start.anio_primera_cuota

        #Crear Impacto Contable
        Move = Pool().get('account.move')
        Period = Pool().get('account.period')
        Currency = Pool().get('currency.currency')
        Date = Pool().get('ir.date')

        accounting_date = Date.today()
        company = Transaction().context.get('company')
        period_id = Period.find(company, date=accounting_date)        
        journal_id = 8 #Pagos
       
            
        Sequence = Pool().get('ir.sequence')

        move, = Move.create([{
                        'journal': journal_id,
                        'period': period_id,
                        'date': accounting_date,
                        'description': 'Prestamo ' + str(self.start.asociada.name),
                        'lines': [
                            ('create', [{
                                        'account': self.start.cuenta_debito.id,
                                        'debit': Decimal(self.start.monto_prestamo),                               
                                        'credit': Decimal('0.0'),
                                        'party': self.start.asociada,
                                        'description': 'Prestamo' + str(self.start.asociada.name),
                                        }, {
                                        'account': self.start.cuenta_credito.id,
                                        'debit':Decimal('0.0'),
                                        'credit':Decimal(self.start.monto_prestamo),
                                        'party': self.start.asociada,
                                        'description': 'Prestamo' + str(self.start.asociada.name),
                                        }]),
                            ],
                        }])
        
        move.save()
      
        for i in range(1, self.start.cantidad_cuotas+1):  
            vencimiento_actual = date(anio_actual,mes_actual,self.start.dia_vencimiento)  
            nueva_cuota = CuotaPrestamo(
                mes = mes_actual,
                anio = anio_actual,
                monto = valor_cuota_con_interes,
                porcentaje_interes = self.start.interes_mensual,
                interes = monto_interes_mensual,
                pagada = False,
                fecha_vencimiento = vencimiento_actual,
                asociada = self.start.asociada,
                monto_total_prestamo = self.start.monto_prestamo,
                cantidad_cuotas = self.start.cantidad_cuotas,
                mes_primera_cuota = self.start.mes_primera_cuota,
                anio_primera_cuota = self.start.anio_primera_cuota,
                cuenta_debito = self.start.cuenta_debito,
                cuenta_credito = self.start.cuenta_credito,
                fecha_creacion = accounting_date,
                )
            nueva_cuota.save()
            if mes_actual == 12:
                mes_actual = 1
                anio_actual += 1
            else:
                mes_actual += 1
        
       

        post_number = Sequence.get_id(move.period.post_move_sequence_used.id)
        move.post_number = post_number
        move.post_date = accounting_date
        move.state = 'posted' 
        move.save()
          
        
        return 'end'
