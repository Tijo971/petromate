from django import forms
from django.forms import inlineformset_factory
from .models import*


class CalibrationChartForm(forms.ModelForm):
    class Meta:
        model = CalibrationChart
        fields = [
            'tank_volume',
            'tank_capacity',
            'length',
            'radious',
            'diameter',
            'difference',
        ]

        widgets = {
            'tank_volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tank volume',
                'required': 'required',
            }),
            'tank_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tank capacity',
                'required': 'required',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter length',
                'required': 'required',
            }),

            'radious': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Radius',
                'required': 'required',
            }),
            'diameter': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter diameter',
                'required': 'required',
            }),
            'difference': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields required explicitly
        for field_name in ['tank_volume', 'tank_capacity', 'length', 'diameter','radious','difference']:
            self.fields[field_name].required = True
            self.fields[field_name].widget.attrs['required'] = 'required'



class CalibrationChartEntryForm(forms.ModelForm):
    class Meta:
        model = CalibrationChartEntry
        fields = ['dip', 'volume', 'difference']

        widgets = {
            'dip': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Dip',
                'required': 'required',
            }),
            'volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Volume',
                'required': 'required',
            }),
            'difference': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Difference',
                'required': 'required',
            }),
        }


from django import forms
from .models import*

# Product Category
class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = productcategory
        fields = ['category_type', 'description', 'is_active']

        widgets = {
            'category_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter short description',
                'required': 'required',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'is_active'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicit required fields
        self.fields['category_type'].required = True
        self.fields['description'].required = True

    # ==========================
    # ✅ DUPLICATE VALIDATION
    # ==========================
    def clean(self):
        cleaned_data = super().clean()

        category_type = cleaned_data.get('category_type')
        description = cleaned_data.get('description')

        if category_type and description:
            qs = productcategory.objects.filter(
                description=description
            )

            # Exclude current record during edit
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "This Category/Type with the same description already exists."
                )

        return cleaned_data



# Tank Master

from django import forms
from .models import TankMaster, CalibrationChart


class TankMasterForm(forms.ModelForm):

    class Meta:
        model = TankMaster
        fields = ['tank_name', 'tank_volume', 'is_active']

        widgets = {
            'tank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tank name',
                'required': 'required',
            }),

            'tank_volume': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'is_active'
                
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required fields
        self.fields['tank_name'].required = True
        self.fields['tank_volume'].required = True

        # 🔹 Show ONLY tank_volume value in select
        self.fields['tank_volume'].queryset = CalibrationChart.objects.all().order_by('tank_volume')
        self.fields['tank_volume'].label_from_instance = (
            lambda obj: f"{obj.tank_volume}"
        )

        # 🔹 Optional: add a single default option
        self.fields['tank_volume'].empty_label = "Select Tank Volume"



# Group master form


class GroupMasterForm(forms.ModelForm):
    class Meta:
        model = GroupMaster
        fields = ['under_group', 'group_name']

        widgets = {
            'under_group': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make fields required explicitly
        self.fields['under_group'].required = True
        self.fields['under_group'].widget.attrs['required'] = 'required'

        self.fields['group_name'].required = True
        self.fields['group_name'].widget.attrs['required'] = 'required'



# LedgerMaster Form

from django import forms
from django.utils import timezone
from .models import LedgerMaster

class LedgerMasterForm(forms.ModelForm):
    class Meta:
        model = LedgerMaster
        fields = ['under_group', 'ledger_name', 'opening_balance', 'dr_cr', 'date']

        widgets = {
            'under_group': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'ledger_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ledger name',
                'required': 'required',
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter opening balance',
                'required': 'required',
                'step': '0.01',
            }),
            'dr_cr': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make fields required explicitly
        self.fields['under_group'].required = True
        self.fields['ledger_name'].required = True
        self.fields['opening_balance'].required = True
        self.fields['dr_cr'].required = True
        self.fields['date'].required = True

        # Set default date to today if not already set
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()

        # Only display 'under_group' field value, not group_name
        self.fields['under_group'].queryset = GroupMaster.objects.all().order_by('under_group')
        self.fields['under_group'].label_from_instance = lambda obj: obj.under_group
    
        self.fields['dr_cr'].empty_label = None

        # ✅ Add only ONE custom first option
        self.fields['dr_cr'].choices = [
            ('', 'Select DR/CR'),
        ] + [
            ('Dr', 'Dr'),
            ('Cr', 'Cr'),
        ]


# Mode of pay form

from django import forms
from .models import ModeOfPay, LedgerMaster

class ModeOfPayForm(forms.ModelForm):
    class Meta:
        model = ModeOfPay
        fields = ['bill_type_name', 'ledger', 'is_active']

        widgets = {
            'bill_type_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Bill Type Name',
                'required': 'required',
            }),
            'ledger': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicitly required fields
        self.fields['bill_type_name'].required = True
        self.fields['ledger'].required = True

        # Ledger dropdown ordering
        self.fields['ledger'].queryset = LedgerMaster.objects.all().order_by('ledger_name')

        # Show only ledger_name in select dropdown
        self.fields['ledger'].label_from_instance = lambda obj: obj.ledger_name

        # Custom first option
        self.fields['ledger'].empty_label = "Select Ledger"



from django import forms
from .models import TaxMaster

class TaxMasterForm(forms.ModelForm):
    class Meta:
        model = TaxMaster
        fields = ['tax_value']

        widgets = {
            'tax_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Tax Value',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicitly set tax_name as required
        self.fields['tax_value'].required = True



from django import forms
from .models import VehicleType


class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['vehicle_type', 'is_active']

        widgets = {
            'vehicle_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Vehicle Type',
                'required': 'required',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicitly set vehicle_type as required
        self.fields['vehicle_type'].required = True


# Product Master

from django import forms
from .models import Entry


class EntryForm(forms.ModelForm):

    entry_type = forms.ChoiceField(
        choices=[('', 'Add Type')] + list(Entry.ENTRY_TYPE_CHOICES),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'addType',
        })
    )

    class Meta:
        model = Entry
        fields = ['entry_type']




from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = [
            'company_name',
            'short_name',
            'address',
            'website',
            'is_supplier',
            # 'is_used',
        ]

        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Company Name',
                
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Short Name',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter Address',
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
            'is_supplier': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_used': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicit required fields
        self.fields['company_name'].required = True

        # # Optional: default flags
        # self.fields['is_used'].initial = True





from django import forms
from django.utils import timezone
from .models import Product, productcategory, TankMaster


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'company',
            'bill_code',
            'product_name',
            'pack',
            'hsn_code',
            'reorder_level',

            'product_type',
            'category',

            'sales_gst',
            'purchase_gst',
            
            'st_percent',  # NEW FIELD

            'tank_applicable',
            'multiple_tank',
            'tank',

            'rate_change_fully',
            'set_stock',
            'initial_stock_date',
        ]

        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'bill_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Bill Code'
            }),
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Name'
            }),
            'pack': forms.NumberInput(attrs={'class': 'form-control'}),
            'hsn_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HSN Code'
            }),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),

            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),

            'sales_gst': forms.Select(attrs={'class': 'form-select'}),
            'purchase_gst': forms.Select(attrs={'class': 'form-select'}),

            'st_percent': forms.Select(attrs={'class': 'form-select'}),  # NEW FIELD

            'tank_applicable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multiple_tank': forms.Select(attrs={'class': 'form-select'}),
            'tank': forms.Select(attrs={'class': 'form-select'}),

            'rate_change_fully': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'set_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'initial_stock_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required fields
        self.fields['company'].required = False
        self.fields['bill_code'].required = True
        self.fields['product_name'].required = True
        self.fields['product_type'].required = True
        self.fields['category'].required = True
        self.fields['st_percent'].required = True  # NEW FIELD REQUIRED

        # 🔹 Product Type dropdown (category_type = 'type')
        self.fields['product_type'].queryset = productcategory.objects.filter(
            category_type='type'
        ).order_by('description')
        self.fields['product_type'].label_from_instance = lambda obj: obj.description

        # 🔹 Category dropdown (category_type = 'category')
        self.fields['category'].queryset = productcategory.objects.filter(
            category_type='category'
        ).order_by('description')
        self.fields['category'].label_from_instance = lambda obj: obj.description

        # Tank dropdown
        self.fields['tank'].queryset = TankMaster.objects.all().order_by('tank_name')

        # Default date
        self.fields['initial_stock_date'].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()

        product_type = cleaned_data.get('product_type')
        multiple_tank = cleaned_data.get('multiple_tank')
        tank_applicable = cleaned_data.get('tank_applicable')

        if product_type and product_type.description.lower() == 'fuel':
            cleaned_data['tank_applicable'] = True

            if not multiple_tank:
                self.add_error(
                'multiple_tank',
                'Multiple tank selection is required for Fuel products.'
                )
        else:
            cleaned_data['multiple_tank'] = None
            cleaned_data['tank_applicable'] = False

        return cleaned_data




from django import forms
from .models import ProductStock


class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = [
            'stock_qty',
            'loose_qty',
            'cost_price',
            'landing_cost',
            'mrp',
            'selling_price',
        ]
        widgets = {
            'stock_qty': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock Quantity'}),
            'loose_qty': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Loose Quantity'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cost Price'}),
            'landing_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Landing Cost'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'MRP'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        mrp = cleaned_data.get('mrp')

        if cost_price:
            cleaned_data['landing_cost'] = cost_price
        if mrp:
            cleaned_data['selling_price'] = mrp

        return cleaned_data



from django import forms
from .models import ProductTankStock, TankMaster


class ProductTankStockForm(forms.ModelForm):
    class Meta:
        model = ProductTankStock
        fields = ['tank', 'stock']

        widgets = {
            'tank': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Stock Quantity',
                'step': '0.01',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order tanks nicely
        self.fields['tank'].queryset = TankMaster.objects.all().order_by('tank_name')

        # Labels
        self.fields['tank'].label = "Tank Name"
        self.fields['stock'].label = "Stock"




from django import forms
from .models import FuelNozzleEntry


class FuelNozzleEntryForm(forms.ModelForm):

    fuelnozilentry = forms.ChoiceField(
        choices=[('', 'Add Type')] + list(FuelNozzleEntry.ENTRY_TYPE_CHOICES),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'fuelTypeSelect'
        })
    )

    class Meta:
        model = FuelNozzleEntry
        fields = ['fuelnozilentry']
        




from django import forms
from .models import FuelEntry


from django import forms
from django.core.exceptions import ValidationError
from .models import FuelEntry


class FuelEntryForm(forms.ModelForm):

    class Meta:
        model = FuelEntry
        fields = [
            'tank',
            'fuel_type',
            'tank_specify',
            'is_active',
            'is_used',
        ]

        widgets = {
            'tank': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'tank_specify': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_used': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tank'].required = True
        self.fields['fuel_type'].required = True
        self.fields['tank_specify'].required = True
        self.fields['is_active'].initial = True

    # 🔐 UNIQUE VALIDATION
    def clean(self):
        cleaned_data = super().clean()

        tank = cleaned_data.get('tank')
        fuel_type = cleaned_data.get('fuel_type')

        if not tank or not fuel_type:
            return cleaned_data

        qs = FuelEntry.objects.filter(
            tank=tank,
            fuel_type=fuel_type
        )

        # 🔄 Exclude self while updating
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError({
                'fuel_type': 'This tank already has this fuel type assigned.',
            })

        return cleaned_data



from django import forms
from .models import NozzleEntry


class NozzleEntryForm(forms.ModelForm):

    class Meta:
        model = NozzleEntry
        fields = [
            'tank',
            'nozzle_name',
            'serial',
            'close_reading',
            'is_active',
            'is_used',
        ]

        widgets = {
            'tank': forms.Select(attrs={
                'class': 'form-select',
                'id': 'tankSelect'  # ✅ FORCE ID
            }),
            'nozzle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Nozzle Name',
            }),
            'serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Serial Number',
            }),
            'close_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Enter Close Reading',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_used': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicit required fields
        self.fields['tank'].required = True
        self.fields['nozzle_name'].required = True
        self.fields['serial'].required = True
        self.fields['close_reading'].required = True

        # Optional defaults
        self.fields['is_active'].initial = True




from django import forms
from .models import FuelRate, Product
class FuelRateForm(forms.ModelForm):
    fuel_type = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select Fuel",  # <-- This will be the first option
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        })
    )

    class Meta:
        model = FuelRate
        fields = ['fuel_type', 'rate', 'date', 'time', 'is_active', 'is_used']

        widgets = {
            'rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fuel rate',
                'step': '0.01',
                'required': 'required',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_used': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fuel_type'].required = True
        self.fields['rate'].required = True




from django import forms
from django.core.validators import RegexValidator
from .models import Staff
from datetime import date


class StaffForm(forms.ModelForm):

    # =========================
    # Custom Validators
    # =========================
    mobile = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Enter a valid 10-digit mobile number",
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Mobile Number'
        })
    )

    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                
            }
        )
    )

    class Meta:
        model = Staff
        fields = [
            'staff_name',
            'address',
            'phone',
            'mobile',
            'open_balance',
            'dr_cr',
            'date',
            'nozzle_applicable',
            'is_active'
        ]

        widgets = {
            'staff_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Staff Name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Mobile Number'
            }),
            'open_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'dr_cr': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            'nozzle_applicable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    
    
    
    # =========================
    # Field Level Validations
    # =========================
    def clean_staff_name(self):
        name = self.cleaned_data.get('staff_name')
        if not name.strip():
            raise forms.ValidationError("Staff name cannot be empty")
        return name

    def clean_open_balance(self):
        balance = self.cleaned_data.get('open_balance')
        if balance < 0:
            raise forms.ValidationError("Opening balance cannot be negative")
        return balance

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Phone number must contain only digits")
            if len(phone) < 6:
                raise forms.ValidationError("Phone number is too short")
        return phone
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    # =========================
    # Form Level Validation
    # =========================
    def clean(self):
        cleaned_data = super().clean()

        nozzle_applicable = cleaned_data.get('nozzle_applicable')
        is_active = cleaned_data.get('is_active')

        if nozzle_applicable and not is_active:
            raise forms.ValidationError(
                "Inactive staff cannot have nozzle allocation"
            )

        return cleaned_data


from django import forms
from .models import NozzleAllocation
from masters.models import NozzleEntry


class NozzleAllocationForm(forms.ModelForm):

    nozzle_entry = forms.ModelChoiceField(
        queryset=NozzleEntry.objects.filter(is_active=True),
        empty_label="Select Nozzle",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_nozzle_entry'
        })
    )

    tank_name = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_tank_name'
        })
    )

    product_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'id': 'id_product_name'
        })
    )

    class Meta:
        model = NozzleAllocation
        fields = [
            'nozzle_entry',
            'nozzle_name',
            'tank_name',
            'product_name',
            'is_active'
        ]

        widgets = {
            'nozzle_name': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_nozzle_name'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    # =========================
    # Dynamic Field Population
    # =========================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nozzle_name'].required = True
        self.fields['tank_name'].required = True
        self.fields['product_name'].required = True

        # If editing existing record
        if self.instance.pk and self.instance.nozzle_entry:
            nozzle = self.instance.nozzle_entry

            self.fields['nozzle_name'].widget.choices = [
                (nozzle.nozzle_name, nozzle.nozzle_name)
            ]
            self.fields['tank_name'].widget.choices = [
                (nozzle.tank_name, nozzle.tank_name)
            ]

    # =========================
    # Validation
    # =========================
    def clean(self):
        cleaned_data = super().clean()

        nozzle_entry = cleaned_data.get('nozzle_entry')
        nozzle_name = cleaned_data.get('nozzle_name')
        tank_name = cleaned_data.get('tank_name')

        if nozzle_entry:
            if nozzle_name != nozzle_entry.nozzle_name:
                self.add_error(
                    'nozzle_name',
                    "Nozzle name does not match selected nozzle"
                )

            if tank_name != nozzle_entry.tank_name:
                self.add_error(
                    'tank_name',
                    "Tank name does not match selected nozzle"
                )

            cleaned_data['product_name'] = nozzle_entry.product_name

        return cleaned_data






from django import forms
from django.utils import timezone
from .models import Supplier
import re


class SupplierForm(forms.ModelForm):

    supplier_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Supplier Name'
        })
    )

    # ✅ MOBILE NUMBER – REQUIRED (default validation)
    mobile = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Mobile Number'
        })
    )

    # ✅ PHONE NUMBER – OPTIONAL (default validation)
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Phone Number'
        })
    )

    open_balance = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Enter Opening Balance'
        })
    )

    dr_cr = forms.ChoiceField(
        choices=Supplier.DR_CR_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Supplier
        fields = [
            'supplier_name',
            'address',
            'phone',
            'mobile',
            'contact_person',
            'contact_person_mobile',
            'gst_no',
            'pan',
            'tan',
            'open_balance',
            'dr_cr',
            'credit_period_days',
            'customer',
            'interstate_supplier',
            'remark',
            'date',
            'is_active'
        ]

        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter Address'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Contact Person'
            }),
            'contact_person_mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Contact Person Mobile Number'
            }),
            'gst_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter GST Number'
            }),
            'pan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PAN Number'
            }),
            'tan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter TAN Number'
            }),
            'credit_period_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Credit Period in Days'
            }),
            'customer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'interstate_supplier': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remark': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter Remarks'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # =========================
    # Field Validations
    # =========================

    def clean_supplier_name(self):
        name = self.cleaned_data.get('supplier_name')

        if not re.match(r'^[A-Za-z\s]+$', name):
            raise forms.ValidationError(
                "Supplier Name must contain only letters and spaces"
            )
        return name

    def clean_open_balance(self):
        balance = self.cleaned_data.get('open_balance')
        if balance is None:
            raise forms.ValidationError("Open Balance is required")
        return balance

    def clean_dr_cr(self):
        dr_cr = self.cleaned_data.get('dr_cr')
        if not dr_cr:
            raise forms.ValidationError("Please select Dr or Cr")
        return dr_cr

    def clean_date(self):
        date = self.cleaned_data.get('date')
        return date or timezone.now().date()
