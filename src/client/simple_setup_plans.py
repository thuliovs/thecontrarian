#!/usr/bin/env python3
"""
Script simplificado para configurar os planos Standard e Premium
apenas com os campos que existem no banco de dados atual
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

def setup_basic_plans():
    """
    Configura os planos Standard e Premium usando apenas os campos
    que existem na tabela client_planchoice atual
    """
    print("Configurando planos básicos...")
    
    # Verificar se já existem planos
    plans = PlanChoice.objects.all()
    if plans.exists():
        print(f"Existem {plans.count()} planos configurados. Atualizando...")
        
        # Atualizar planos existentes
        for plan in plans:
            print(f"Verificando plano: {plan.name}")
            
            if getattr(plan, 'plan_code', None) == 'ST' or (hasattr(plan, 'plan') and plan.plan == 'ST'):
                plan.name = 'Standard'
                plan.cost = Decimal('2.99')
                plan.is_active = True
                plan.description = 'Standard Plan - Access to basic articles'
                plan.save()
                print("Plano Standard atualizado!")
                
            elif getattr(plan, 'plan_code', None) == 'PR' or (hasattr(plan, 'plan') and plan.plan == 'PR'):
                plan.name = 'Premium'
                plan.cost = Decimal('9.99')
                plan.is_active = True
                plan.description = 'Premium Plan - Access to all content'
                plan.save()
                print("Plano Premium atualizado!")
        
        return
    
    # Criar novo plano Standard
    try:
        plan_st = PlanChoice()
        
        # Verificar se devemos usar plan_code ou plan
        if hasattr(PlanChoice, 'plan_code'):
            plan_st.plan_code = 'ST'
        else:
            plan_st.plan = 'ST'
            
        plan_st.name = 'Standard'
        plan_st.cost = Decimal('2.99')
        plan_st.is_active = True
        plan_st.description = 'Standard Plan - Access to basic articles'
        plan_st.save()
        print("Plano Standard criado!")
    except Exception as e:
        print(f"Erro ao criar plano Standard: {e}")
    
    # Criar novo plano Premium
    try:
        plan_pr = PlanChoice()
        
        # Verificar se devemos usar plan_code ou plan
        if hasattr(PlanChoice, 'plan_code'):
            plan_pr.plan_code = 'PR'
        else:
            plan_pr.plan = 'PR'
            
        plan_pr.name = 'Premium'
        plan_pr.cost = Decimal('9.99')
        plan_pr.is_active = True
        plan_pr.description = 'Premium Plan - Access to all content'
        plan_pr.save()
        print("Plano Premium criado!")
    except Exception as e:
        print(f"Erro ao criar plano Premium: {e}")
    
    print("Configuração básica de planos concluída!")

if __name__ == "__main__":
    setup_basic_plans() 