from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

# Create your views here.
class salesreturnview(TemplateView):
    template_name = "transactions/salesreturn.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class openingbalanceview(TemplateView):
    template_name = "transactions/openingbalance.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class creditsaleview(TemplateView):
    template_name = "transactions/creditsale.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class individualsaleview(TemplateView):
    template_name = "transactions/individualsale.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class managepurchaseview(TemplateView):
    template_name = "transactions/procurement/managepurchase.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class purchasereturnview(TemplateView):
    template_name = "transactions/procurement/purchasereturn.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class generateinvoicerview(TemplateView):
    template_name = "transactions/generateinvoice.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    


class billingview(TemplateView):
    template_name = "transactions/billing.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class dipentryview(TemplateView):
    template_name = "transactions/dipentry.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class tankdencityview(TemplateView):
    template_name = "transactions/tankdencity.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class tankerdensityview(TemplateView):
    template_name = "transactions/tankerdensity.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class transaction(TemplateView):
    template_name = "transactions/transactionfull.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
