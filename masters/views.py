from itertools import product
from multiprocessing import context
from aiohttp import request
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import*
from .forms import*
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.db import transaction

# Create your views here.

class baseview(TemplateView):
    template_name = "masters/dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class productcategoryview(TemplateView):

    template_name = "masters/productcategory.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_category_type = productcategory.objects.all().order_by('-id')

        paginator = Paginator(all_category_type, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        packagetype_id = self.request.GET.get('edit')
        form = None
        editing_packagetype = None

        if packagetype_id:
            try:
                editing_packagetype = productcategory.objects.get(id=packagetype_id)
                form = ProductCategoryForm(instance=editing_packagetype)
                context['editing_packagetype'] = editing_packagetype
            except productcategory.DoesNotExist:
                messages.error(self.request, 'Category/Type not found!')

        if not form:
            form = ProductCategoryForm()

        context.update({
            'form': form,
            'packages': page_obj,
            'queryset': page_obj,
            'total_packagetype': all_category_type.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        packagetype_id = request.POST.get('packagetype_id')

        if packagetype_id:
            package_instance = get_object_or_404(productcategory, id=packagetype_id)
            form = ProductCategoryForm(request.POST, instance=package_instance)
        else:
            package_instance = None
            form = ProductCategoryForm(request.POST)

        if form.is_valid():
            category_type = form.cleaned_data.get('category_type')
            description = form.cleaned_data.get('description')

            # ✅ DUPLICATE CHECK
            if category_type and description:
                duplicate_qs = productcategory.objects.filter(
                    category_type=category_type,
                    description__iexact=description  # case-insensitive check
                )
                if packagetype_id:
                    duplicate_qs = duplicate_qs.exclude(id=packagetype_id)

                if duplicate_qs.exists():
                    context = self.get_context_data()
                    context['form'] = form
                    context['editing_packagetype'] = package_instance if packagetype_id else None
                    context['duplicate_error'] = "This Category/Type with the same description already exists."
                    return self.render_to_response(context)

            # Save the instance
            package_instance = form.save(commit=False)

            if 'is_active' not in request.POST:
                package_instance.is_active = False

            if packagetype_id:
                package_instance.updated_by = request.user
                action = "updated"
            else:
                package_instance.created_by = request.user
                package_instance.updated_by = request.user
                action = "created"

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            package_instance.ip_address = (
                x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            )

            package_instance.save()
            messages.success(request, f'Category/Type {action} successfully!')
            return redirect('masters:productcategory')

        # Form invalid
        context = self.get_context_data()
        context['form'] = form
        if packagetype_id:
            context['editing_packagetype'] = get_object_or_404(productcategory, id=packagetype_id)
        return self.render_to_response(context)



# ==================== DELETE VIEW ====================

# @login_required
def delete_package_type(request, pk):
    if request.method == 'POST':
        cat_type = get_object_or_404(productcategory, pk=pk)
        cat_type.delete()
        messages.success(request, 'Category/Type deleted successfully!')
        return redirect('masters:productcategory')

    return redirect('masters:productcategory')


# ==================== EXPORT VIEW ====================

# @login_required
def export_package_types(request, export_type):
    package = productcategory.objects.all().order_by('category_type')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Product_Category.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Category/Type', 'Description', 'Status', 'Created At'])

        for idx, pack in enumerate(package, 1):
            writer.writerow([
                idx,
                pack.get_category_type_display(),
                pack.description or '',
                'Active' if pack.is_active else 'Inactive',
                pack.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Product_Category.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Product Category")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 720, "Product Category List")

        data = [['S.No', 'Category/Type', 'Description', 'Status']]

        for idx, pack in enumerate(package, 1):
            description = (pack.description or '')
            if len(description) > 50:
                description = description[:50] + "..."

            data.append([
                str(idx),
                pack.get_category_type_display(),
                description or 'N/A',
                'Active' if pack.is_active else 'Inactive'
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:productcategory')



    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    





class tankmasterview(TemplateView):
    template_name = "masters/tankmaster.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ FIXED HERE
        all_tanks = TankMaster.objects.select_related('tank_volume').order_by('-id')

        paginator = Paginator(all_tanks, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        tank_id = self.request.GET.get('edit')
        form = None
        editing_tank = None

        if tank_id:
            try:
                editing_tank = TankMaster.objects.get(id=tank_id)
                form = TankMasterForm(instance=editing_tank)
                context['editing_tank'] = editing_tank
            except TankMaster.DoesNotExist:
                messages.error(self.request, 'Tank not found!')

        if not form:
            form = TankMasterForm()

        context.update({
            'form': form,
            'tanks': page_obj,
            'queryset': page_obj,
            'total_tanks': all_tanks.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        tank_id = request.POST.get('tank_id')

        if tank_id:
            tank_instance = get_object_or_404(TankMaster, id=tank_id)
            form = TankMasterForm(request.POST, instance=tank_instance)
        else:
            form = TankMasterForm(request.POST)

        if form.is_valid():
            tank_instance = form.save(commit=False)

            if 'is_active' not in request.POST:
                tank_instance.is_active = False

            try:
                if tank_id:
                    tank_instance.updated_by = request.user
                    action = "updated"
                else:
                    tank_instance.created_by = request.user
                    tank_instance.updated_by = request.user
                    action = "created"
            except Exception:
                action = "saved"

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            tank_instance.ip_address = (
                x_forwarded_for.split(',')[0].strip()
                if x_forwarded_for else request.META.get('REMOTE_ADDR')
            )

            tank_instance.save()
            messages.success(request, f'Tank {action} successfully!')
            return redirect('masters:tankmaster')

        context = self.get_context_data()
        context['form'] = form

        if tank_id:
            context['editing_tank'] = get_object_or_404(TankMaster, id=tank_id)

        return self.render_to_response(context)

# ==================== DELETE VIEW ====================

# @login_required
def delete_tank(request, pk):
    if request.method == 'POST':
        tank = get_object_or_404(TankMaster, pk=pk)
        tank.delete()
        messages.success(request, 'Tank deleted successfully!')
        return redirect('masters:tankmaster')

    return redirect('masters:tankmaster')


# ==================== EXPORT VIEW ====================

# @login_required
def export_tanks(request, export_type):
    tanks = TankMaster.objects.select_related('tank_volume').all().order_by('tank_name')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Tanks.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Tank Name', 'Tank Volume', 'Status', 'Created At'])

        for idx, t in enumerate(tanks, 1):
            # tank_volume is a FK to CalibrationChart — using str() to be safe
            tank_volume_display = str(t.tank_volume) if t.tank_volume else ''
            writer.writerow([
                idx,
                t.tank_name or '',
                tank_volume_display,
                'Active' if t.is_active else 'Inactive',
                (t.created_at.strftime('%Y-%m-%d %H:%M:%S') if getattr(t, 'created_at', None) else '')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Tanks.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Tank Master")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Tank Master List")

        data = [['S.No', 'Tank Name', 'Tank Volume', 'Status']]

        for idx, t in enumerate(tanks, 1):
            tank_volume_display = str(t.tank_volume) if t.tank_volume else 'N/A'
            data.append([
                str(idx),
                t.tank_name or 'N/A',
                tank_volume_display,
                'Active' if t.is_active else 'Inactive'
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:tankmaster')
    




from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import FuelRate
from .forms import FuelRateForm


class FuelRateView(TemplateView):
    template_name = "masters/managefuelrate.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Queryset
        all_fuel_rates = FuelRate.objects.select_related('fuel_type').order_by('-date', '-time')

        # Pagination
        paginator = Paginator(all_fuel_rates, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        fuelrate_id = self.request.GET.get('edit')
        form = None
        editing_fuelrate = None

        if fuelrate_id:
            try:
                editing_fuelrate = FuelRate.objects.get(id=fuelrate_id)
                form = FuelRateForm(instance=editing_fuelrate)
                context['editing_fuelrate'] = editing_fuelrate
            except FuelRate.DoesNotExist:
                messages.error(self.request, 'Fuel rate not found!')

        if not form:
            form = FuelRateForm()


        

        context.update({
            'form': form,
            'fuel_rates': page_obj,
            'queryset': page_obj,
            'total_fuel_rates': all_fuel_rates.count(),
            
        })

        return context

    def post(self, request, *args, **kwargs):
        fuelrate_id = request.POST.get('fuelrate_id')

        if fuelrate_id:
            # Update
            fuelrate_instance = get_object_or_404(FuelRate, id=fuelrate_id)
            form = FuelRateForm(request.POST, instance=fuelrate_instance)
            action = "updated"
        else:
            # Create
            form = FuelRateForm(request.POST)
            action = "created"

        if form.is_valid():
            fuelrate_instance = form.save(commit=False)

            # Checkbox handling
            if 'is_active' not in request.POST:
                fuelrate_instance.is_active = False
            if 'is_used' not in request.POST:
                fuelrate_instance.is_used = False

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            fuelrate_instance.ip_address = (
                x_forwarded_for.split(',')[0]
                if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            fuelrate_instance.save()
            messages.success(request, f'Fuel rate {action} successfully!')
            return redirect('masters:fuel_rate')

        # Form invalid
        context = self.get_context_data()
        context['form'] = form

        if fuelrate_id:
            context['editing_fuelrate'] = get_object_or_404(FuelRate, id=fuelrate_id)

        return self.render_to_response(context)
    

def export_fuel_rates(request, export_type):
    # Fetch fuel rate entries
    fuel_rates = (
        FuelRate.objects
        .select_related('fuel_type')
        .order_by('-id')
    )

    # ==========================
    # EXCEL EXPORT
    # ==========================
    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Fuel_Rates.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'S.No',
            'Fuel Type',
            'Rate',
            'Date',
            'Time',
            'Status'
        ])

        for idx, rate in enumerate(fuel_rates, 1):
            writer.writerow([
                idx,
                rate.fuel_type.product_name,
                rate.rate,
                rate.date.strftime('%d-%m-%Y') if rate.date else '',
                rate.time.strftime('%I:%M %p') if rate.time else '',
                'Active' if rate.is_active else 'Inactive'
            ])

        return response

    # ==========================
    # PDF EXPORT
    # ==========================
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Fuel_Rates.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph("Fuel Rate List", styles['Title'])
        elements.append(title)

        data = [[
            'S.No',
            'Fuel Type',
            'Rate',
            'Date',
            'Time',
            'Status'
        ]]

        for idx, rate in enumerate(fuel_rates, 1):
            data.append([
                str(idx),
                rate.fuel_type.product_name,
                str(rate.rate),
                rate.date.strftime('%d-%m-%Y') if rate.date else '',
                rate.time.strftime('%I:%M %p') if rate.time else '',
                'Active' if rate.is_active else 'Inactive'
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)
        return response

    return redirect('masters:fuel_rate_master')



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import FuelRate

def delete_fuel_rate(request, pk):
    if request.method == 'POST':
        fuel_rate = get_object_or_404(FuelRate, pk=pk)

        # Optional: Prevent deletion if in use
        if fuel_rate.is_used:
            messages.warning(request, 'Cannot delete this Fuel Rate because it is in use.')
        else:
            fuel_rate.delete()
            messages.success(request, 'Fuel Rate deleted successfully!')

        return redirect('masters:fuel_rate')  # Update with your Fuel Rate list URL name

    # If GET or other method, just redirect
    return redirect('masters:fuel_rate')



class NozzleStaffAllocPageView(TemplateView):
    template_name = "masters/nozil_stf_alloc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["staff_list"] = Staff.objects.prefetch_related(
            "nozzle_allocations"
        ).order_by("staff_name")

        context["tank_entries"] = FuelEntry.objects.select_related(
            "tank", "fuel_type"
        )

        context["nozzle_entries"] = NozzleEntry.objects.filter(
            is_active=True
        )

        return context




    
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Staff, NozzleAllocation, NozzleEntry

class NozzleStaffAllocSaveView(View):

    def post(self, request, *args, **kwargs):

        staff_id = request.POST.get("staff_id")

        if not staff_id or staff_id == "all-staffs":
            return JsonResponse({
                "success": False,
                "message": "Please select a valid staff"
            }, status=400)

        staff = get_object_or_404(Staff, pk=staff_id)

        nozzle_names = request.POST.getlist("nozzle_name[]")
        tank_names = request.POST.getlist("tank_name[]")
        product_names = request.POST.getlist("product_name[]")

        if not nozzle_names:
            return JsonResponse({
                "success": False,
                "message": "Please add at least one allocation"
            }, status=400)

        try:
            with transaction.atomic():
                # Delete existing allocations for the staff
                NozzleAllocation.objects.filter(staff=staff).delete()

                # Create new allocations
                for i, nozzle_name in enumerate(nozzle_names):
                    nozzle_entry = NozzleEntry.objects.filter(
                        nozzle_name=nozzle_name,
                        is_active=True
                    ).first()

                    if not nozzle_entry:
                        raise ValueError(f"Invalid nozzle: {nozzle_name}")

                    NozzleAllocation.objects.create(
                        staff=staff,
                        nozzle_entry=nozzle_entry,
                        nozzle_name=nozzle_name,
                        tank_name=tank_names[i],
                        product_name=product_names[i] if i < len(product_names) else "",
                        is_active=True
                    )

                # ✅ Update staff field nozzle_applicable
                staff.nozzle_applicable = 1
                staff.save(update_fields=['nozzle_applicable'])

            return JsonResponse({
                "success": True,
                "message": "Nozzle allocation saved successfully"
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=500)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from .models import NozzleAllocation, Staff  # adjust import if needed


import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import NozzleAllocation, Staff

def nozzle_staff_alloc_delete(request):
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"success": False, "message": "Invalid request"})

    data = json.loads(request.body)
    alloc_id = data.get("allocation_id")

    allocation = get_object_or_404(NozzleAllocation, pk=alloc_id)
    staff = allocation.staff  # Get the staff before deleting

    allocation.delete()

    # ✅ Update staff nozzle_applicable field to 0 if no allocations left
    if not NozzleAllocation.objects.filter(staff=staff).exists():
        staff.nozzle_applicable = 0
        staff.save(update_fields=['nozzle_applicable'])

    return JsonResponse({"success": True, "message": "Allocation deleted"})



from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction

from .models import Entry, Company, Product, ProductStock
from .forms import EntryForm, CompanyForm, ProductForm, ProductStockForm


from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages

from .models import (
    Entry, Company, Product, ProductStock,
    ProductTankStock, TankMaster
)
from .forms import (
    EntryForm, CompanyForm, ProductForm, ProductStockForm
)


class EntryMasterView(TemplateView):
    template_name = "masters/pdt_master.html"

    # ==========================
    # GET
    # ==========================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # All entries
        entries_qs = Entry.objects.all().order_by('-id')

        # Separate company and product querysets
        companies_qs = Company.objects.select_related('entry').order_by('-id')
        products_qs = Product.objects.select_related('entry').order_by('-id')

        # Pagination
        entries_page = Paginator(entries_qs, 10).get_page(self.request.GET.get('page_entries'))
        companies_page = Paginator(companies_qs, 10).get_page(self.request.GET.get('page_companies'))
        products_page = Paginator(products_qs, 10).get_page(self.request.GET.get('page_products'))

        edit_id = self.request.GET.get('edit')
        editing_entry = None
        tank_stocks = None

        if edit_id:
            editing_entry = get_object_or_404(Entry, id=edit_id)
            entry_form = EntryForm(instance=editing_entry)

            if editing_entry.entry_type == 'company':
                company = Company.objects.filter(entry=editing_entry).first()
                company_form = CompanyForm(instance=company)
                product_form = ProductForm()
                stock_form = ProductStockForm()

            else:  # PRODUCT
                product = Product.objects.filter(entry=editing_entry).first()
                stock = ProductStock.objects.filter(product=product).first()
                product_form = ProductForm(instance=product)
                stock_form = ProductStockForm(instance=stock)
                company_form = CompanyForm()
                tank_stocks = ProductTankStock.objects.filter(product=product)

        else:
            entry_form = EntryForm()
            company_form = CompanyForm()
            product_form = ProductForm()
            stock_form = ProductStockForm()

        context.update({
            'entries': entries_page,          # all entries
            'companies': companies_page,      # paginated companies
            'products': products_page,        # paginated products
            'entry_form': entry_form,
            'company_form': company_form,
            'product_form': product_form,
            'stock_form': stock_form,
            'editing_entry': editing_entry,
            'tank_stocks': tank_stocks,
            'tank_list': TankMaster.objects.all().order_by('tank_name'),
        })
        return context
    
    # ==========================
    # POST
    # ==========================
    def post(self, request, *args, **kwargs):

        entry_id = request.POST.get('entry_id')
        entry_instance = Entry.objects.filter(id=entry_id).first()

        entry_form = EntryForm(request.POST, instance=entry_instance)

        company_instance = Company.objects.filter(entry=entry_instance).first()
        product_instance = Product.objects.filter(entry=entry_instance).first()
        stock_instance = ProductStock.objects.filter(product=product_instance).first()

        company_form = CompanyForm(request.POST, request.FILES, instance=company_instance)
        product_form = ProductForm(request.POST, request.FILES, instance=product_instance)
        stock_form = ProductStockForm(request.POST, instance=stock_instance)

        if not entry_form.is_valid():
            return self._invalid(entry_form, company_form, product_form, stock_form)

        try:
            with transaction.atomic():

                entry = entry_form.save()
                is_update = bool(entry_instance)

                # ==========================
                # COMPANY
                # ==========================
                if entry.entry_type == 'company':

                    if not company_form.is_valid():
                        return self._invalid(entry_form, company_form, product_form, stock_form)

                    company = company_form.save(commit=False)
                    company.entry = entry
                    company.ip_address = self._get_ip()
                    company.save()

                    Product.objects.filter(entry=entry).delete()
                    ProductTankStock.objects.filter(product__entry=entry).delete()

                # ==========================
                # PRODUCT
                # ==========================
                elif entry.entry_type == 'product':

                    if not product_form.is_valid():
                        print("❌ PRODUCT FORM ERRORS:", product_form.errors)
                        return self._invalid(entry_form, company_form, product_form, stock_form)

                    product = product_form.save(commit=False)
                    product.entry = entry
                    product.ip_address = self._get_ip()
                    product.company = product_form.cleaned_data.get('company')
                    product.save()

                    # --------------------------
                    # SINGLE STOCK
                    # --------------------------
                    if product.set_stock:
                        stock_instance = ProductStock.objects.filter(product=product).first()
                        stock_form = ProductStockForm(request.POST, instance=stock_instance)

                        if not stock_form.is_valid():
                            print("❌ STOCK FORM ERRORS:", stock_form.errors)
                            return self._invalid(entry_form, company_form, product_form, stock_form)

                        stock = stock_form.save(commit=False)
                        stock.product = product
                        stock.save()
                    else:
                        ProductStock.objects.filter(product=product).delete()

                    # --------------------------
                    # MULTIPLE TANK STOCK
                    # --------------------------
                    ProductTankStock.objects.filter(product=product).delete()

                    tank_ids = request.POST.getlist('tank[]')
                    stocks = request.POST.getlist('stock[]')

                    for tank_id, stock_qty in zip(tank_ids, stocks):
                        if not tank_id or not stock_qty:
                            continue

                        ProductTankStock.objects.create(
                            product=product,
                            tank_id=tank_id,
                            stock=stock_qty
                        )

                    Company.objects.filter(entry=entry).delete()

                messages.success(
                    request,
                    f"Entry {'updated' if is_update else 'created'} successfully!"
                )
                return redirect('masters:entry_master')

        except Exception as e:
            messages.error(request, f"Save failed: {e}")
            return redirect('masters:entry_master')

    # ==========================
    # INVALID FORM
    # ==========================
    def _invalid(self, entry_form, company_form, product_form, stock_form):
        context = self.get_context_data()
        context.update({
            'entry_form': entry_form,
            'company_form': company_form,
            'product_form': product_form,
            'stock_form': stock_form,
        })
        return self.render_to_response(context)

    # ==========================
    # IP
    # ==========================
    def _get_ip(self):
        return (
            self.request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
            or self.request.META.get('REMOTE_ADDR')
        )



class EntryDeleteView(View):
    def post(self, request, pk):
        entry = get_object_or_404(Entry, pk=pk)
        entry.delete()
        messages.success(request, "Entry deleted successfully")
        return redirect('masters:entry_master')


class ProductStockDeleteView(View):
    """
    Deletes a single ProductTankStock row (tank stock).
    """

    def post(self, request, pk):
        tank_stock = get_object_or_404(ProductTankStock, pk=pk)

        try:
            tank_stock.delete()
            messages.success(request, "Tank stock deleted successfully")
        except Exception as e:
            messages.error(request, f"Failed to delete tank stock: {e}")

        return redirect('masters:entry_master') 



class ProductDeleteView(View):
    def post(self, request, pk):
        """
        Delete a Product and its associated ProductStock entries.
        """
        product = get_object_or_404(Product, pk=pk)

        # Delete related stock entries first
        ProductStock.objects.filter(product=product).delete()

        # Delete the product
        product.delete()

        messages.success(request, "Product deleted successfully")
        return redirect('masters:entry_master')
    

def export_companies(request, export_type):
    # Fetch only company entries
    companies = Entry.objects.filter(entry_type='company').order_by('-id')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Companies.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Company Name'])

        for idx, entry in enumerate(companies, 1):
            company_name = entry.company.company_name if hasattr(entry, 'company') else 'N/A'
            writer.writerow([idx, company_name])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Companies.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Company List")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Company List")

        # Table data
        data = [['S.No', 'Company Name']]
        for idx, entry in enumerate(companies, 1):
            company_name = entry.company.company_name if hasattr(entry, 'company') else 'N/A'
            data.append([str(idx), company_name])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:entry_master')



def export_products(request, export_type):
    # Fetch only product entries
    products = Entry.objects.filter(entry_type='product').order_by('-id')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Products.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Bill Code', 'Product Name', 'HSN Code', 'Pack', 'MRP', 'Selling Price'])

        for idx, entry in enumerate(products, 1):
            product = entry.product if hasattr(entry, 'product') else None
            stock = product.stock_entries.first() if product else None

            writer.writerow([
                idx,
                product.bill_code if product else '-',
                product.product_name if product else '-',
                product.hsn_code if product else '-',
                product.pack if product else '-',
                stock.mrp if stock else '-',
                stock.selling_price if stock else '-'
            ])
        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Products.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title = Paragraph("Product List", styles['Title'])
        elements.append(title)

        # Table data
        data = [['S.No', 'Bill Code', 'Product Name', 'HSN Code', 'Pack', 'MRP', 'Selling Price']]
        for idx, entry in enumerate(products, 1):
            product = getattr(entry, 'product', None)
            stock = product.stock_entries.first() if product else None
            data.append([
                str(idx),
                getattr(product, 'bill_code', '-'),
                getattr(product, 'product_name', '-'),
                getattr(product, 'hsn_code', '-'),
                getattr(product, 'pack', '-'),
                str(getattr(stock, 'mrp', '-')),
                str(getattr(stock, 'selling_price', '-')),
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d3d3d3')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
        return response

    return redirect('masters:entry_master')



class FuelNozzleMasterView(TemplateView):
    template_name = "masters/tank_nozil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        entries_qs = FuelNozzleEntry.objects.select_related(
            'fuel_entry__tank',
            'fuel_entry__fuel_type',
            'nozzle_entry__tank'
        ).order_by('-id')

        context['entries'] = Paginator(
            entries_qs, 10
        ).get_page(self.request.GET.get('page'))

        fuel_qs = FuelNozzleEntry.objects.filter(
            fuelnozilentry='fuel'
        ).select_related(
            'fuel_entry__tank',
            'fuel_entry__fuel_type'
        ).order_by('-id')

        context['fuel_entries'] = Paginator(
            fuel_qs, 10
        ).get_page(self.request.GET.get('fuel_page'))

        nozzle_qs = FuelNozzleEntry.objects.filter(
            fuelnozilentry='nozzle'
        ).select_related(
            'nozzle_entry__tank'
        ).order_by('-id')

        context['nozzle_entries'] = Paginator(
            nozzle_qs, 10
        ).get_page(self.request.GET.get('nozzle_page'))

        edit_id = self.request.GET.get('edit')
        editing_entry = None

        if edit_id:
            editing_entry = get_object_or_404(FuelNozzleEntry, id=edit_id)
            entry_form = FuelNozzleEntryForm(instance=editing_entry)

            if editing_entry.fuelnozilentry == 'fuel':
                fuel_form = FuelEntryForm(
                    instance=FuelEntry.objects.filter(
                        fuel_nozzle_entry=editing_entry
                    ).first()
                )
                nozzle_form = NozzleEntryForm()
            else:
                nozzle_form = NozzleEntryForm(
                    instance=NozzleEntry.objects.filter(
                        fuel_nozzle_entry=editing_entry
                    ).first()
                )
                fuel_form = FuelEntryForm()
        else:
            entry_form = FuelNozzleEntryForm()
            fuel_form = FuelEntryForm()
            nozzle_form = NozzleEntryForm()

        context.update({
            'entry_form': entry_form,
            'fuel_form': fuel_form,
            'nozzle_form': nozzle_form,
            'editing_entry': editing_entry,
            'tank_list': TankMaster.objects.order_by('tank_name'),
        })

        return context

    # ==========================
    # POST
    # ==========================
    def post(self, request, *args, **kwargs):

        entry_id = request.POST.get('entry_id')
        entry_instance = FuelNozzleEntry.objects.filter(id=entry_id).first()

        entry_form = FuelNozzleEntryForm(
            request.POST, instance=entry_instance
        )

        fuel_instance = (
            FuelEntry.objects.filter(
                fuel_nozzle_entry=entry_instance
            ).first() if entry_instance else None
        )

        nozzle_instance = (
            NozzleEntry.objects.filter(
                fuel_nozzle_entry=entry_instance
            ).first() if entry_instance else None
        )

        fuel_form = FuelEntryForm(request.POST, instance=fuel_instance)
        nozzle_form = NozzleEntryForm(request.POST, instance=nozzle_instance)

        if not entry_form.is_valid():
            return self._invalid(entry_form, fuel_form, nozzle_form)

        try:
            with transaction.atomic():

                # ==========================
                # 🚫 FUEL DUPLICATE CHECK (BEFORE SAVE)
                # ==========================
                if entry_form.cleaned_data['fuelnozilentry'] == 'fuel':

                    if not fuel_form.is_valid():
                        return self._invalid(
                            entry_form, fuel_form, nozzle_form
                        )

                    tank = fuel_form.cleaned_data['tank']

                    qs = FuelEntry.objects.filter(tank=tank)
                    if fuel_instance:
                        qs = qs.exclude(pk=fuel_instance.pk)

                    if qs.exists():
                        messages.error(
                            request,
                            "This tank already has a fuel entry. "
                            "Only one fuel per tank is allowed."
                        )
                        return redirect('masters:fuel_nozzle_master')

                # ==========================
                # ✅ SAFE TO SAVE ENTRY NOW
                # ==========================
                entry = entry_form.save()
                is_update = bool(entry_instance)

                if entry.fuelnozilentry == 'fuel':
                    fuel = fuel_form.save(commit=False)
                    fuel.fuel_nozzle_entry = entry
                    fuel.ip_address = self._get_ip()
                    fuel.save()

                    NozzleEntry.objects.filter(
                        fuel_nozzle_entry=entry
                    ).delete()

                else:
                    nozzle = nozzle_form.save(commit=False)
                    nozzle.fuel_nozzle_entry = entry
                    nozzle.ip_address = self._get_ip()
                    nozzle.save()

                    FuelEntry.objects.filter(
                        fuel_nozzle_entry=entry
                    ).delete()

                messages.success(
                    request,
                    f"{entry.fuelnozilentry.title()} entry "
                    f"{'updated' if is_update else 'created'} successfully!"
                )
                return redirect('masters:fuel_nozzle_master')

        except Exception as e:
            messages.error(request, f"Save failed: {e}")
            return redirect('masters:fuel_nozzle_master')

    def _invalid(self, entry_form, fuel_form, nozzle_form):
        context = self.get_context_data()
        context.update({
            'entry_form': entry_form,
            'fuel_form': fuel_form,
            'nozzle_form': nozzle_form,
        })
        return self.render_to_response(context)

    def _get_ip(self):
        request = self.request
        return request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR')
        )




from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import FuelEntry, FuelNozzleEntry


class FuelEntryDeleteView(View):
    def post(self, request, pk):
        """
        Delete FuelEntry and its related FuelNozzleEntry safely.
        """
        fuel_entry = get_object_or_404(FuelEntry, pk=pk)

        try:
            with transaction.atomic():

                # ✅ Delete related FuelNozzleEntry FIRST
                FuelNozzleEntry.objects.filter(
                    fuel_entry=fuel_entry
                ).delete()

                # ✅ Then delete FuelEntry
                fuel_entry.delete()

            messages.success(request, "Fuel entry deleted successfully")

        except Exception as e:
            messages.error(request, f"Failed to delete fuel entry: {e}")

        return redirect('masters:fuel_nozzle_master')





from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import FuelNozzleEntry, FuelEntry, NozzleEntry


class FuelNozzleDeleteView(View):
    def post(self, request, pk):
        """
        Delete Fuel or Nozzle entry along with FuelNozzleEntry safely.
        """
        entry = get_object_or_404(FuelNozzleEntry, pk=pk)

        try:
            with transaction.atomic():

                if entry.fuelnozilentry == 'fuel':
                    # ✅ Delete related FuelEntry first
                    FuelEntry.objects.filter(
                        fuel_nozzle_entry=entry
                    ).delete()

                elif entry.fuelnozilentry == 'nozzle':
                    # ✅ Delete related NozzleEntry first
                    NozzleEntry.objects.filter(
                        fuel_nozzle_entry=entry
                    ).delete()

                # ✅ Finally delete FuelNozzleEntry
                entry.delete()

            messages.success(
                request,
                f"{entry.fuelnozilentry.title()} entry deleted successfully"
            )

        except Exception as e:
            messages.error(request, f"Delete failed: {e}")

        return redirect('masters:fuel_nozzle_master')


from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import csv

from .models import FuelNozzleEntry


def export_fuel_entries(request, export_type):
    """
    Export Fuel Entry Report (Excel / PDF)
    """

    # ✅ Fetch only fuel entries with related FuelEntry
    entries = FuelNozzleEntry.objects.select_related(
        'fuel_entry',
        'fuel_entry__tank',
        'fuel_entry__fuel_type'
    ).filter(
        fuelnozilentry='fuel',
        fuel_entry__isnull=False
    ).order_by('-id')

    # ==========================
    # EXCEL
    # ==========================
    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Fuel_Entry_Report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'S.No',
            'Tank',
            'Fuel Type',
            'Capacity',
            'Status'
        ])

        for idx, entry in enumerate(entries, 1):
            fuel = entry.fuel_entry
            writer.writerow([
                idx,
                fuel.tank.tank_name if fuel.tank else 'N/A',
                fuel.fuel_type.product_name if fuel.fuel_type else 'N/A',
                fuel.tank.tank_volume if fuel.tank else 'N/A',
                'Active' if fuel.is_active else 'Inactive'
            ])

        return response

    # ==========================
    # PDF
    # ==========================
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Fuel_Entry_Report.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Fuel Entry Report")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Fuel Entry Report")

        data = [[
            'S.No',
            'Tank',
            'Fuel Type',
            'Capacity',
            'Status'
        ]]

        for idx, entry in enumerate(entries, 1):
            fuel = entry.fuel_entry
            data.append([
                str(idx),
                fuel.tank.tank_name if fuel.tank else 'N/A',
                fuel.fuel_type.product_name if fuel.fuel_type else 'N/A',
                str(fuel.tank.tank_volume) if fuel.tank else 'N/A',
                'Active' if fuel.is_active else 'Inactive'
            ])

        table = Table(data, colWidths=[40, 120, 120, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 500, 600)
        table.drawOn(p, 40, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:fuel_nozzle_master')



from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import csv

from .models import FuelNozzleEntry


def export_nozzle_fuel_entries(request, export_type):
    """
    Export Nozzle Fuel Entry Report (Excel / PDF)
    """

    # ✅ Fetch only nozzle entries with related NozzleEntry
    entries = FuelNozzleEntry.objects.select_related(
        'nozzle_entry'
    ).filter(
        fuelnozilentry='nozzle',
        nozzle_entry__isnull=False
    ).order_by('-id')

    # ==========================
    # EXCEL
    # ==========================
    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Nozzle_Entry_Report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'S.No',
            'Nozzle Name',
            'Serial',
            'Close Reading',
            'Status'
        ])

        for idx, entry in enumerate(entries, 1):
            nozzle = entry.nozzle_entry
            writer.writerow([
                idx,
                nozzle.nozzle_name if nozzle else 'N/A',
                nozzle.serial if nozzle else 'N/A',
                nozzle.close_reading if nozzle else 'N/A',
                'Active' if nozzle.is_active else 'Inactive'
            ])

        return response

    # ==========================
    # PDF
    # ==========================
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Nozzle_Entry_Report.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Nozzle Entry Report")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Nozzle Entry Report")

        data = [[
            'S.No',
            'Nozzle Name',
            'Serial',
            'Close Reading',
            'Status'
        ]]

        for idx, entry in enumerate(entries, 1):
            nozzle = entry.nozzle_entry
            data.append([
                str(idx),
                nozzle.nozzle_name if nozzle else 'N/A',
                nozzle.serial if nozzle else 'N/A',
                str(nozzle.close_reading) if nozzle else 'N/A',
                'Active' if nozzle.is_active else 'Inactive'
            ])

        table = Table(data, colWidths=[40, 120, 100, 100, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 500, 600)
        table.drawOn(p, 40, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:fuel_nozzle_master')




# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import TankMaster, FuelEntry


def get_tank_details(request, tank_id):
    tank = get_object_or_404(TankMaster, pk=tank_id)

    fuel_entry = FuelEntry.objects.filter(
        tank=tank
    ).select_related('fuel_type').first()

    # ✅ Extract readable capacity from CalibrationChart
    capacity = ""
    if tank.tank_volume:
        capacity = str(tank.tank_volume)  # uses __str__() of CalibrationChart

    return JsonResponse({
        'fuel_type': fuel_entry.fuel_type.product_name
            if fuel_entry and fuel_entry.fuel_type else '',
        'capacity': capacity
    })





class VehicleTypeMasterView(TemplateView):
    template_name = "masters/crm/vehicle_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # QuerySet
        all_vehicle_types = VehicleType.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_vehicle_types, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        vehicle_type_id = self.request.GET.get('edit')
        form = None
        editing_vehicle_type = None

        if vehicle_type_id:
            try:
                editing_vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
                form = VehicleTypeForm(instance=editing_vehicle_type)
                context['editing_vehicle_type'] = editing_vehicle_type
            except VehicleType.DoesNotExist:
                messages.error(self.request, 'Vehicle Type not found!')

        if not form:
            form = VehicleTypeForm()

        context.update({
            'form': form,
            'queryset': page_obj,
            'vehicle_types': page_obj,
            'total_vehicle_types': all_vehicle_types.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        vehicle_type_id = request.POST.get('vehicle_type_id')

        if vehicle_type_id:
            vehicle_type_instance = get_object_or_404(VehicleType, id=vehicle_type_id)
            form = VehicleTypeForm(request.POST, instance=vehicle_type_instance)
        else:
            form = VehicleTypeForm(request.POST)

        if form.is_valid():
            vehicle_type_instance = form.save(commit=False)

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            vehicle_type_instance.ip_address = (
                x_forwarded_for.split(',')[0]
                if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            vehicle_type_instance.save()

            action = "updated" if vehicle_type_id else "created"
            messages.success(request, f'Vehicle Type {action} successfully!')
            return redirect('masters:vehicle_type_master')

        # Invalid form
        context = self.get_context_data()
        context['form'] = form

        if vehicle_type_id:
            context['editing_vehicle_type'] = get_object_or_404(
                VehicleType, id=vehicle_type_id
            )

        return self.render_to_response(context)
    
    # Delete VehicleType

def delete_vehicle_type(request, pk):
    if request.method == 'POST':
        vehicle_type = get_object_or_404(VehicleType, pk=pk)

        if vehicle_type.is_used:
            messages.error(request, 'This Vehicle Type is already in use and cannot be deleted!')
            return redirect('masters:vehicle_type_master')

        vehicle_type.delete()
        messages.success(request, 'Vehicle Type deleted successfully!')
        return redirect('masters:vehicle_type_master')

    return redirect('masters:vehicle_type_master')

# expoet pdf and excel

def export_vehicle_type_master(request, export_type):
    vehicle_types = VehicleType.objects.all().order_by('vehicle_type')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Vehicle_Type_Master.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Vehicle Type', 'Active', 'Created At'])

        for idx, vt in enumerate(vehicle_types, 1):
            writer.writerow([
                idx,
                vt.vehicle_type,
                'Yes' if vt.is_active else 'No',
                vt.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Vehicle_Type_Master.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Vehicle Type Master")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Vehicle Type Master List")

        data = [['S.No', 'Vehicle Type', 'Active']]

        for idx, vt in enumerate(vehicle_types, 1):
            data.append([
                str(idx),
                vt.vehicle_type,
                'Yes' if vt.is_active else 'No'
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 50, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:vehicle_type_master')


    
class managecustomerview(TemplateView):
    template_name = "masters/crm/manage_customer.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class indentissueview(TemplateView):
    template_name = "masters/crm/indent_issue.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class customeroutstandingview(TemplateView):
    template_name = "masters/crm/cus_outstanding.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Supplier, LedgerMaster
from .forms import SupplierForm


class SupplierView(TemplateView):
    template_name = "masters/suppliers/mnge_suppliers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        suppliers_qs = Supplier.objects.all().order_by('-created_at')

        paginator = Paginator(suppliers_qs, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        supplier_id = self.request.GET.get('edit')
        form = None
        editing_supplier = None

        if supplier_id:
            editing_supplier = get_object_or_404(Supplier, id=supplier_id)
            form = SupplierForm(instance=editing_supplier)
            context['editing_supplier'] = editing_supplier

        if not form:
            form = SupplierForm()

        context.update({
            'form': form,
            'suppliers': page_obj,
            'total_suppliers': suppliers_qs.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        supplier_id = request.POST.get('supplier_id')

        if supplier_id:
            supplier_instance = get_object_or_404(Supplier, id=supplier_id)
            form = SupplierForm(request.POST, instance=supplier_instance)
            action = "updated"
        else:
            form = SupplierForm(request.POST)
            action = "created"

        if not form.is_valid():
            print("FORM ERRORS 👉", form.errors)  # DEBUG
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

        supplier_instance = form.save(commit=False)

        # ===============================
        # 🔴 REQUIRED LEDGER ASSIGNMENT
        # ===============================
        ledger = LedgerMaster.objects.first()
        if not ledger:
            messages.error(request, "LedgerMaster not found. Please create one first.")
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

        supplier_instance.ledger = ledger  # ✅ REQUIRED

        # ===============================
        # Checkbox handling
        # ===============================
        supplier_instance.customer = 'customer' in request.POST
        supplier_instance.interstate_supplier = 'interstate_supplier' in request.POST
        supplier_instance.is_active = 'is_active' in request.POST

        # ===============================
        # IP Address
        # ===============================
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        supplier_instance.ip_address = (
            x_forwarded_for.split(',')[0]
            if x_forwarded_for
            else request.META.get('REMOTE_ADDR')
        )

        supplier_instance.save()
        messages.success(request, f"Supplier {action} successfully!")
        return redirect('masters:supplier')


#   Delete Supplier

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_supplier(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, pk=pk)

        if supplier.is_used:
            messages.error(
                request,
                'This Supplier is already in use and cannot be deleted!'
            )
            return redirect('masters:supplier')

        supplier.delete()
        messages.success(
            request,
            'Supplier deleted successfully!'
        )
        return redirect('masters:supplier')

    return redirect('masters:supplier')




import csv
from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from .models import Supplier


def export_supplier_master(request, export_type):
    suppliers = Supplier.objects.all().order_by('supplier_name')

    # =======================
    # EXPORT TO EXCEL (CSV)
    # =======================
    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Supplier_Master.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Sl.No',
            'Supplier Name',
            'Mobile',
            'Status'
        ])

        for idx, supplier in enumerate(suppliers, 1):
            writer.writerow([
                idx,
                supplier.supplier_name,
                supplier.mobile or '',
                'Active' if supplier.is_active else 'Inactive'
            ])

        return response

    # =======================
    # EXPORT TO PDF
    # =======================
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Supplier_Master.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Supplier Master")

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, "Supplier Master List")

        # Table Data
        data = [['Sl.No', 'Supplier Name', 'Mobile', 'Status']]

        for idx, supplier in enumerate(suppliers, 1):
            data.append([
                str(idx),
                supplier.supplier_name,
                supplier.mobile or '',
                'Active' if supplier.is_active else 'Inactive'
            ])

        table = Table(data, colWidths=[50, 200, 120, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))

        table.wrapOn(p, 500, 600)
        table.drawOn(p, 40, 650)

        p.showPage()
        p.save()
        return response

    return redirect('masters:supplier')



class supplieroutstandingview(TemplateView):
    template_name = "masters/suppliers/suplers_outstanding.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    



from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages

from .models import (
    Staff,
    NozzleAllocation,
    NozzleEntry,
    TankMaster
)
from .forms import StaffForm


from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages

from .models import Staff, NozzleEntry, NozzleAllocation, TankMaster
from .forms import StaffForm

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.db.models import Prefetch


from .models import (
    Staff,
    NozzleEntry,
    NozzleAllocation,
    TankMaster,
    Product,
)
from .forms import StaffForm


class StaffMasterView(TemplateView):
    template_name = "masters/staffs/managestaffs.html"

    # =========================
    # GET
    # =========================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # =========================
        # Staff list with pagination
        # =========================
        staff_qs = Staff.objects.all().order_by("-id")
        paginator = Paginator(staff_qs, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # =========================
        # Edit staff
        # =========================
        staff_id = self.request.GET.get("edit")
        staff_form = None
        editing_staff = None
        nozzle_allocations = []

        if staff_id:
            editing_staff = Staff.objects.filter(id=staff_id).first()
            if editing_staff:
                staff_form = StaffForm(instance=editing_staff)
                nozzle_allocations = editing_staff.nozzle_allocations.all()

        if not staff_form:
            staff_form = StaffForm()

        # =========================
        # ✅ COMBINED TANK + PRODUCT + NOZZLE (FIXED)
        # =========================
        tank_entries = TankMaster.objects.filter(
            is_active=True
                    ).prefetch_related(
                Prefetch(
                    "products",   # ← real related_name
                        queryset=Product.objects.filter(tank__is_active=True),
                        to_attr="tank_products"   # ✅ renamed
                     ),
                Prefetch(
                        "nozzle_entries",   # ← real related_name
                            queryset=NozzleEntry.objects.filter(
                            is_active=True
                            ).order_by("nozzle_name"),
                            to_attr="tank_nozzles"    # ✅ renamed
                                )
                    )

        # =========================
        # CONTEXT
        # =========================
        context.update({
            "staff_form": staff_form,
            "staff_list": page_obj,
            "total_staff": staff_qs.count(),

            # 🔑 Combined data via common tank_id
            "tank_entries": tank_entries,

            "editing_staff": editing_staff,
        "nozzle_allocations": nozzle_allocations,
        })

        return context

    # =========================
    # POST
    # =========================
    def post(self, request, *args, **kwargs):
        staff_id = request.POST.get("staff_id")

    # Create / Update staff
        if staff_id:
            staff_instance = get_object_or_404(Staff, id=staff_id)
            staff_form = StaffForm(request.POST, instance=staff_instance)
        else:
            staff_form = StaffForm(request.POST)

        if not staff_form.is_valid():
            return self.render_to_response(
                self._error_context(staff_form, staff_id)
            )

        try:
            with transaction.atomic():

            # =====================
            # SAVE STAFF
            # =====================
                staff = staff_form.save(commit=False)
                staff.ip_address = request.META.get("REMOTE_ADDR")
                staff.save()

            # =====================
            # CLEAR OLD ALLOCATIONS
            # =====================
                NozzleAllocation.objects.filter(staff=staff).delete()

            # =====================
            # SAVE NEW ALLOCATIONS
            # =====================
                if staff.nozzle_applicable:

                    nozzle_names = request.POST.getlist("nozzle_name[]")
                    tank_ids = request.POST.getlist("tank_id[]")

                    for nozzle_name, tank_id in zip(nozzle_names, tank_ids):

                        if not nozzle_name or not tank_id:
                            continue

                    # 🔑 Validate Tank
                        tank = TankMaster.objects.filter(
                            id=tank_id,
                            is_active=True
                        ).first()

                        if not tank:
                            raise ValueError("Invalid tank selected")

                    # 🔑 Validate Nozzle belongs to Tank
                        nozzle_entry = NozzleEntry.objects.filter(
                            tank=tank,
                            nozzle_name=nozzle_name,
                            is_active=True
                        ).first()

                        if not nozzle_entry:
                            raise ValueError(
                                f"Nozzle '{nozzle_name}' does not belong to tank '{tank.tank_name}'"
                            )

                    # 🔑 Product for same tank
                        product = Product.objects.filter(
                            tank=tank
                        ).first()

                        NozzleAllocation.objects.create(
                            staff=staff,
                            nozzle_entry=nozzle_entry,
                            nozzle_name=nozzle_name,
                            tank_name=tank.tank_name,
                            product_name=product.product_name if product else "",
                            is_active=True
                        )
            messages.success(request, "Staff saved successfully")
            return redirect("masters:staffmaster")

        except Exception as e:
            messages.error(request, str(e))
            return redirect("masters:staffmaster")

    
    
    # =========================
    # ERROR CONTEXT
    # =========================
    def _error_context(self, staff_form, staff_id):
        context = self.get_context_data()
        context["staff_form"] = staff_form

        if staff_id:
            context["editing_staff"] = get_object_or_404(
                Staff, id=staff_id
            )

        return context




def delete_staff(request, pk):
    """
    Delete Staff and its related Nozzle Allocations
    """
    staff = get_object_or_404(Staff, pk=pk)

    # Related nozzle allocations will be deleted automatically
    # because of on_delete=models.CASCADE
    staff.delete()

    messages.success(request, "Staff deleted successfully!")
    return redirect('masters:staffmaster')




import csv
from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from .models import Staff

def export_staff_list(request, export_type):
    staff_list = Staff.objects.all().order_by('-id')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Staff_List.csv"'

        writer = csv.writer(response)
        writer.writerow(['Sl.No', 'Staff Name', 'Mobile', 'Nozzle Applicable', 'Status'])

        for idx, staff in enumerate(staff_list, 1):
            writer.writerow([
                idx,
                staff.staff_name,
                staff.mobile,
                'Yes' if staff.nozzle_applicable else 'No',
                'Active' if staff.is_active else 'Inactive'
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Staff_List.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Staff List")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Staff List")

        # Table data
        data = [['Sl.No', 'Staff Name', 'Mobile', 'Nozzle Applicable', 'Status']]
        for idx, staff in enumerate(staff_list, 1):
            data.append([
                str(idx),
                staff.staff_name,
                staff.mobile,
                'Yes' if staff.nozzle_applicable else 'No',
                'Active' if staff.is_active else 'Inactive'
            ])

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 500, 700)
        table.drawOn(p, 50, 600)  # Adjust X,Y to fit page nicely

        p.showPage()
        p.save()
        return response

    return redirect('masters:staffmaster')





class CalibrationChartView(TemplateView):
    template_name = "masters/charts/calibration_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # All charts ordered by latest
        all_charts = CalibrationChart.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_charts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Check if we are editing an existing chart
        chart_id = self.request.GET.get('edit')
        form = None
        editing_chart = None

        if chart_id:
            editing_chart = CalibrationChart.objects.filter(id=chart_id).first()
            if editing_chart:
                form = CalibrationChartForm(instance=editing_chart)
                context['entries'] = editing_chart.entries.all()
                context['editing_chart'] = editing_chart
            else:
                messages.error(self.request, 'Calibration Chart not found!')

        if not form:
            form = CalibrationChartForm()

        context.update({
            'form': form,
            'charts': page_obj,
            'total_charts': all_charts.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        chart_id = request.POST.get('chart_id')
        chart_instance = None

        if chart_id:
            chart_instance = get_object_or_404(CalibrationChart, id=chart_id)
            form = CalibrationChartForm(request.POST, instance=chart_instance)
        else:
            form = CalibrationChartForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                chart = form.save(commit=False)

            # Capture user IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                chart.ip_address = (
                    x_forwarded_for.split(',')[0].strip()
                    if x_forwarded_for else request.META.get('REMOTE_ADDR')
                )
                chart.save()

                dips = request.POST.getlist('dip[]')
                volumes = request.POST.getlist('volume[]')
                differences = request.POST.getlist('difference[]')

            # Clear old entries if updating
                if chart_id:
                    CalibrationChartEntry.objects.filter(calibration_chart=chart).delete()

            # Create new entries
                entries_to_create = []
                for dip, volume, diff in zip(dips, volumes, differences):
                    if dip and volume:
                        entries_to_create.append(
                            CalibrationChartEntry(
                                calibration_chart=chart,
                                dip=dip,
                                volume=volume,
                                difference=diff or 0
                            )
                        )
                CalibrationChartEntry.objects.bulk_create(entries_to_create)

            action = "updated" if chart_id else "created"
            messages.success(self.request, f'Calibration Chart {action} successfully!')
            return redirect('masters:calibrationchart')

    # Invalid form - re-render
        context = self.get_context_data()
        context['form'] = form
        if chart_id:
            context['editing_chart'] = get_object_or_404(CalibrationChart, id=chart_id)

        return self.render_to_response(context)

def delete_calibration_chart(request, pk):
    """Delete a Calibration Chart."""
    if request.method == 'POST':
        chart = get_object_or_404(CalibrationChart, pk=pk)
        chart.delete()
        messages.success(request, 'Calibration Chart deleted successfully!')
    return redirect('masters:calibrationchart')


def export_calibration_chart(request, export_type):
    chart_list = CalibrationChart.objects.all().order_by('tank_volume')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="CalibrationChart.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'tank_volume', 'tank_capacity', 'length', 'radious', 'diameter', 'difference'])

        for idx, chart in enumerate(chart_list, 1):
            writer.writerow([
                idx,
                chart.tank_volume,
                chart.tank_capacity,
                chart.length,
                chart.radious,
                chart.diameter,
                chart.difference,
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="CalibrationChart.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Calibration Chart")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Chart List")

        data = [['S.No', 'Tank Volume', 'Tank Capacity', 'length', 'radious', 'diameter', 'difference']]

        for idx, c in enumerate(chart_list, 1):
            data.append([
                str(idx),
                c.tank_volume,
                c.tank_capacity,
                c.length,
                c.radious,
                c.diameter,
                c.difference,

            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:calibrationchart')



# Dip Table Excel & Pdf

import csv
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from .models import CalibrationChart, CalibrationChartEntry

def export_dip_entries(request, chart_id, export_type):
    """
    Export DIP entries for a specific CalibrationChart
    """
    chart = CalibrationChart.objects.prefetch_related("entries").filter(id=chart_id).first()
    if not chart:
        return HttpResponse("Chart not found", status=404)

    entries = chart.entries.all().order_by("dip")

    # ===== EXCEL EXPORT =====
    if export_type == "excel":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="DIP_Entries_{chart.tank_volume}.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Dip (CM)', 'Volume (LTS)', 'Difference (LTR/MM)'])

        for idx, entry in enumerate(entries, 1):
            writer.writerow([
                idx,
                entry.dip,
                entry.volume,
                entry.difference
            ])

        return response

    # ===== PDF EXPORT =====
    elif export_type == "pdf":
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="DIP_Entries_{chart.tank_volume}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle(f"DIP Entries - {chart.tank_volume}")

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(150, 750, f"DIP Entries - {chart.tank_volume}")

        # Table data
        data = [['S.No', 'Dip (CM)', 'Volume (LTS)', 'Difference (LTR/MM)']]
        for idx, entry in enumerate(entries, 1):
            data.append([
                str(idx),
                str(entry.dip),
                str(entry.volume),
                str(entry.difference)
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ]))

        table.wrapOn(p, 500, 700)
        table.drawOn(p, 50, 700 - (len(data) * 18))

        p.showPage()
        p.save()
        return response

    return HttpResponse("Invalid export type", status=400)

    


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CalibrationChart

def get_dip_by_tank_volume(request):
    chart_id = request.GET.get("chart_id")

    if not chart_id:
        return JsonResponse({"data": []})

    chart = get_object_or_404(CalibrationChart, id=chart_id)

    entries = chart.entries.all().order_by("dip")

    data = []
    prev_volume = None

    for entry in entries:
        diff = float(entry.volume) - float(prev_volume) if prev_volume else 0
        data.append({
            "dip": entry.dip,
            "volume": entry.volume,
            "difference": entry.difference,
        })
        prev_volume = entry.volume

    return JsonResponse({"data": data})



class densitychartview(TemplateView):
    template_name = "masters/charts/density_chart.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)  
    
class resetshiftview(TemplateView):
    template_name = "masters/resetsettlement/resetshift.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class deleteshiftview(TemplateView):
    template_name = "masters/resetsettlement/deleteshift.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    
class GroupMasterView(TemplateView):
    template_name = "masters/accountmasters/groupmaster.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # QuerySet
        all_groups = GroupMaster.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_groups, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        group_id = self.request.GET.get('edit')
        form = None
        editing_group = None

        if group_id:
            try:
                editing_group = GroupMaster.objects.get(id=group_id)
                form = GroupMasterForm(instance=editing_group)
                context['editing_group'] = editing_group
            except GroupMaster.DoesNotExist:
                messages.error(self.request, 'Group not found!')

        if not form:
            form = GroupMasterForm()

        context.update({
            'form': form,
            'queryset': page_obj,
            'groups': page_obj,
            'total_groups': all_groups.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')

        if group_id:
            group_instance = get_object_or_404(GroupMaster, id=group_id)
            form = GroupMasterForm(request.POST, instance=group_instance)
        else:
            form = GroupMasterForm(request.POST)

        if form.is_valid():
            group_instance = form.save(commit=False)

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            group_instance.ip_address = (
                x_forwarded_for.split(',')[0] if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            group_instance.save()

            action = "updated" if group_id else "created"
            messages.success(request, f'Group {action} successfully!')
            return redirect('masters:groupmaster')

        # Invalid form
        context = self.get_context_data()
        context['form'] = form

        if group_id:
            context['editing_group'] = get_object_or_404(GroupMaster, id=group_id)

        return self.render_to_response(context)


# ==================== DELETE VIEW ====================

def delete_group_master(request, pk):
    if request.method == 'POST':
        group = get_object_or_404(GroupMaster, pk=pk)
        group.delete()
        messages.success(request, 'Group deleted successfully!')
        return redirect('masters:groupmaster')

    return redirect('masters:groupmaster')


# ==================== EXPORT VIEW ====================

def export_group_master(request, export_type):
    groups = GroupMaster.objects.all().order_by('under_group')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Group_Master.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Group Name', 'Under Group', 'Created At'])

        for idx, group in enumerate(groups, 1):
            writer.writerow([
                idx,
                group.group_name,
                group.get_under_group_display(),
                group.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Group_Master.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Group Master")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Group Master List")

        data = [['S.No', 'Group Name', 'Under Group']]

        for idx, group in enumerate(groups, 1):
            data.append([
                str(idx),
                group.group_name,
                group.get_under_group_display(),
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:groupmaster')


from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from .models import LedgerMaster, GroupMaster
from .forms import LedgerMasterForm


class LedgerMasterView(TemplateView):
    template_name = "masters/accountmasters/ledgermaster.html"

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # QuerySet
        all_ledgers = LedgerMaster.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_ledgers, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        ledger_id = self.request.GET.get('edit')
        form = None
        editing_ledger = None

        if ledger_id:
            try:
                editing_ledger = LedgerMaster.objects.get(id=ledger_id)
                form = LedgerMasterForm(instance=editing_ledger)
                context['editing_ledger'] = editing_ledger
            except LedgerMaster.DoesNotExist:
                messages.error(self.request, 'Ledger not found!')

        if not form:
            form = LedgerMasterForm()

        context.update({
            'form': form,
            'queryset': page_obj,
            'ledgers': page_obj,
            'total_ledgers': all_ledgers.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        ledger_id = request.POST.get('ledger_id')

        if ledger_id:
            ledger_instance = get_object_or_404(LedgerMaster, id=ledger_id)
            form = LedgerMasterForm(request.POST, instance=ledger_instance)
        else:
            form = LedgerMasterForm(request.POST)

        if form.is_valid():
            ledger_instance = form.save(commit=False)

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ledger_instance.ip_address = (
                x_forwarded_for.split(',')[0] if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            ledger_instance.save()

            action = "updated" if ledger_id else "created"
            messages.success(request, f'Ledger {action} successfully!')
            return redirect('masters:ledgermaster')

        # Invalid form
        context = self.get_context_data()
        context['form'] = form

        if ledger_id:
            context['editing_ledger'] = get_object_or_404(LedgerMaster, id=ledger_id)

        return self.render_to_response(context)


# ==================== DELETE VIEW ====================

def delete_ledger_master(request, pk):
    if request.method == 'POST':
        ledger = get_object_or_404(LedgerMaster, pk=pk)
        ledger.delete()
        messages.success(request, 'Ledger deleted successfully!')
    return redirect('masters:ledgermaster')



# ==================== EXPORT VIEW ====================

def export_ledger_master(request, export_type):
    ledgers = LedgerMaster.objects.all().order_by('ledger_name')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Ledger_Master.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Ledger Name', 'Under Group', 'Opening Balance', 'Dr/Cr', 'Date'])

        for idx, ledger in enumerate(ledgers, 1):
            writer.writerow([
                idx,
                ledger.ledger_name,
                ledger.under_group.get_under_group_display(),
                ledger.opening_balance,
                ledger.get_dr_cr_display(),
                ledger.date.strftime('%Y-%m-%d')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Ledger_Master.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Ledger Master")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Ledger Master List")

        data = [['S.No', 'Ledger Name', 'Under Group', 'Opening Balance', 'Dr/Cr', 'Date']]

        for idx, ledger in enumerate(ledgers, 1):
            data.append([
                str(idx),
                ledger.ledger_name,
                ledger.under_group.get_under_group_display(),
                str(ledger.opening_balance),
                ledger.get_dr_cr_display(),
                ledger.date.strftime('%Y-%m-%d')
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 100, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:ledgermaster')

    
class bankdetailsview(TemplateView):
    template_name = "masters/accountmasters/bankdetails.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
class ModeOfPayView(TemplateView):
    template_name = "masters/adminpanel/modeofpay.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # QuerySet
        all_modes = ModeOfPay.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_modes, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        mode_id = self.request.GET.get('edit')
        form = None
        editing_mode = None

        if mode_id:
            try:
                editing_mode = ModeOfPay.objects.get(id=mode_id)
                form = ModeOfPayForm(instance=editing_mode)
                context['editing_mode'] = editing_mode
            except ModeOfPay.DoesNotExist:
                messages.error(self.request, 'Mode of Pay not found!')

        if not form:
            form = ModeOfPayForm()

        context.update({
            'form': form,
            'queryset': page_obj,
            'modes': page_obj,
            'total_modes': all_modes.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        mode_id = request.POST.get('mode_id')

        if mode_id:
            mode_instance = get_object_or_404(ModeOfPay, id=mode_id)
            form = ModeOfPayForm(request.POST, instance=mode_instance)
        else:
            form = ModeOfPayForm(request.POST)

        if form.is_valid():
            mode_instance = form.save(commit=False)

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            mode_instance.ip_address = (
                x_forwarded_for.split(',')[0]
                if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            mode_instance.save()

            action = "updated" if mode_id else "created"
            messages.success(request, f'Mode of Pay {action} successfully!')
            return redirect('masters:modeofpay')

        # Invalid form
        context = self.get_context_data()
        context['form'] = form

        if mode_id:
            context['editing_mode'] = get_object_or_404(ModeOfPay, id=mode_id)

        return self.render_to_response(context)
    
    # Delete Function

def delete_mode_of_pay(request, pk):
    if request.method == 'POST':
        mode = get_object_or_404(ModeOfPay, pk=pk)
        mode.delete()
        messages.success(request, 'Mode of Pay deleted successfully!')
        return redirect('masters:modeofpay')

    return redirect('masters:modeofpay')

# Expott function
def export_mode_of_pay(request, export_type):
    modes = ModeOfPay.objects.select_related('ledger').all().order_by('bill_type_name')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Mode_Of_Pay.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Bill Type Name', 'Ledger', 'Status', 'Created At'])

        for idx, mode in enumerate(modes, 1):
            writer.writerow([
                idx,
                mode.bill_type_name,
                mode.ledger.ledger_name,
                'Active' if mode.is_active else 'Inactive',
                mode.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Mode_Of_Pay.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Mode of Pay")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Mode of Pay List")

        data = [['S.No', 'Bill Type Name', 'Ledger', 'Status']]

        for idx, mode in enumerate(modes, 1):
            data.append([
                str(idx),
                mode.bill_type_name,
                mode.ledger.ledger_name,
                'Active' if mode.is_active else 'Inactive',
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 50, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:modeofpay')

    

class TaxMasterView(TemplateView):
    template_name = "masters/adminpanel/taxmaster.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # QuerySet
        all_taxes = TaxMaster.objects.all().order_by('-id')

        # Pagination
        paginator = Paginator(all_taxes, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Edit mode
        tax_id = self.request.GET.get('edit')
        form = None
        editing_tax = None

        if tax_id:
            try:
                editing_tax = TaxMaster.objects.get(id=tax_id)
                form = TaxMasterForm(instance=editing_tax)
                context['editing_tax'] = editing_tax
            except TaxMaster.DoesNotExist:
                messages.error(self.request, 'Tax Master not found!')

        if not form:
            form = TaxMasterForm()

        context.update({
            'form': form,
            'queryset': page_obj,
            'taxes': page_obj,
            'total_taxes': all_taxes.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        tax_id = request.POST.get('tax_id')

        if tax_id:
            tax_instance = get_object_or_404(TaxMaster, id=tax_id)
            form = TaxMasterForm(request.POST, instance=tax_instance)
        else:
            form = TaxMasterForm(request.POST)

        if form.is_valid():
            tax_instance = form.save(commit=False)

            # IP Address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            tax_instance.ip_address = (
                x_forwarded_for.split(',')[0]
                if x_forwarded_for
                else request.META.get('REMOTE_ADDR')
            )

            tax_instance.save()

            action = "updated" if tax_id else "created"
            messages.success(request, f'Tax Master {action} successfully!')
            return redirect('masters:taxmaster')

        # Invalid form
        context = self.get_context_data()
        context['form'] = form

        if tax_id:
            context['editing_tax'] = get_object_or_404(TaxMaster, id=tax_id)

        return self.render_to_response(context)


# Delete function
def delete_tax_master(request, pk):
    if request.method == 'POST':
        tax = get_object_or_404(TaxMaster, pk=pk)
        tax.delete()
        messages.success(request, 'Tax Master deleted successfully!')
        return redirect('masters:taxmaster')

    return redirect('masters:taxmaster')


# Export function
def export_tax_master(request, export_type):
    taxes = TaxMaster.objects.all().order_by('tax_value')

    if export_type == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Tax_Master.csv"'

        writer = csv.writer(response)
        writer.writerow(['S.No', 'Tax Name', 'Created At'])

        for idx, tax in enumerate(taxes, 1):
            writer.writerow([
                idx,
                tax.tax_value,
                tax.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Tax_Master.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        p.setTitle("Tax Master")

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Tax Master List")

        data = [['S.No', 'Tax Name']]

        for idx, tax in enumerate(taxes, 1):
            data.append([str(idx), tax.tax_value])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(p, 400, 600)
        table.drawOn(p, 50, 600)

        p.showPage()
        p.save()
        return response

    return redirect('masters:taxmaster') 
    
class stockadjustmentview(TemplateView):
    template_name = "masters/adminpanel/stockadjustment.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
