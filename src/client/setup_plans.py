#!/usr/bin/env python3
"""
Script para configurar os planos Standard e Premium com valores padrão
"""
import os
import sys
import django
from decimal import Decimal

# Configurar ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
django.setup()

from client.models import PlanChoice

def setup_plans():
    """Configura os planos Standard e Premium"""
    print("Configurando planos...")
    
    # Verificar se já existem planos
    plans = PlanChoice.objects.all()
    if plans.exists():
        print(f"Existem {plans.count()} planos configurados")
        
        # Atualizar planos existentes
        for plan in plans:
            print(f"Atualizando plano: {plan.name}")
            
            if plan.plan_code == 'ST':
                plan.name = 'Standard'
                plan.cost = Decimal('2.99')
                plan.is_active = True
                plan.description1 = 'Get access to standard articles and reports'
                plan.description2 = 'Limited access'
                plan.external_plan_id = 'P-5UX16656YT4375159M7A5AKA'
                plan.external_api_url = 'https://www.paypal.com/sdk/js?client-id=AVNwDSxo5q4bqB-Cv8EgeewqLuC_J1KbjCwT6qj0X4_1NDvovQVBbhOTOlCDddaoGbotcN2EoVJLHlL0&vault=true&intent=subscription'
                plan.external_style_json = """{
                    "shape": "pill",
                    "color": "silver",
                    "layout": "vertical",
                    "label": "subscribe"
                }"""
                plan.save()
                print("Plano Standard atualizado!")
                
            elif plan.plan_code == 'PR':
                plan.name = 'Premium'
                plan.cost = Decimal('9.99')
                plan.is_active = True
                plan.description1 = 'Get access to premium articles and reports'
                plan.description2 = 'Unlimited access'
                plan.external_plan_id = 'P-0S100621MM6805235M7A6KVI'
                plan.external_api_url = 'https://www.paypal.com/sdk/js?client-id=AVNwDSxo5q4bqB-Cv8EgeewqLuC_J1KbjCwT6qj0X4_1NDvovQVBbhOTOlCDddaoGbotcN2EoVJLHlL0&vault=true&intent=subscription'
                plan.external_style_json = """{
                    "shape": "pill",
                    "color": "gold",
                    "layout": "vertical",
                    "label": "subscribe"
                }"""
                plan.save()
                print("Plano Premium atualizado!")
        
        return
    
    # Criar plano Standard
    PlanChoice.objects.create(
        plan_code='ST',
        name='Standard',
        cost=Decimal('2.99'),
        is_active=True,
        description1='Get access to standard articles and reports',
        description2='Limited access',
        external_plan_id='P-5UX16656YT4375159M7A5AKA',
        external_api_url='https://www.paypal.com/sdk/js?client-id=AVNwDSxo5q4bqB-Cv8EgeewqLuC_J1KbjCwT6qj0X4_1NDvovQVBbhOTOlCDddaoGbotcN2EoVJLHlL0&vault=true&intent=subscription',
        external_style_json="""{
            "shape": "pill",
            "color": "silver",
            "layout": "vertical",
            "label": "subscribe"
        }"""
    )
    print("Plano Standard criado!")
    
    # Criar plano Premium
    PlanChoice.objects.create(
        plan_code='PR',
        name='Premium',
        cost=Decimal('9.99'),
        is_active=True,
        description1='Get access to premium articles and reports',
        description2='Unlimited access',
        external_plan_id='P-0S100621MM6805235M7A6KVI',
        external_api_url='https://www.paypal.com/sdk/js?client-id=AVNwDSxo5q4bqB-Cv8EgeewqLuC_J1KbjCwT6qj0X4_1NDvovQVBbhOTOlCDddaoGbotcN2EoVJLHlL0&vault=true&intent=subscription',
        external_style_json="""{
            "shape": "pill",
            "color": "gold",
            "layout": "vertical",
            "label": "subscribe"
        }"""
    )
    print("Plano Premium criado!")
    
    print("Configuração de planos concluída!")

if __name__ == "__main__":
    setup_plans() 