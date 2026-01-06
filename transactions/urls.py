from django.urls import path
from .views import *


app_name = 'transactions'


urlpatterns = [
    path('salesreturn/', salesreturnview.as_view(), name='salesreturn'),
    path('openingbalance/', openingbalanceview.as_view(), name='openingbalance'),
    path('creditsale/', creditsaleview.as_view(), name='creditsale'),
    path('individualsale/', individualsaleview.as_view(), name='individualsale'),
    path('managepurchaseview/', managepurchaseview.as_view(), name='managepurchaseview'),
    path('purchasereturn/', purchasereturnview.as_view(), name='purchasereturn'),
    path('generateinvoice/', generateinvoicerview.as_view(), name='generateinvoice'),
    path('billing/', billingview.as_view(), name='billing'),
    path('dipentry/', dipentryview.as_view(), name='dipentry'),
    path('tankdencityview/', tankdencityview.as_view(), name='tankdencityview'),    
    path('tankerdensityview/', tankerdensityview.as_view(), name='tankerdensityview'),    
    path('transaction/', transaction.as_view(), name='transaction'),  
    
    ]