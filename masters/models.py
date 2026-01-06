from django.db import models

class CalibrationChart(models.Model):
    DIFFERENCE_CHOICES = [
        ('calculate', 'Calculate'),
        ('recalculate', 'Recalculate'),
        ('none', 'None'),
    ]

    tank_volume = models.FloatField(
        verbose_name="Tank Volume",
        unique=True,
        null=True,
        blank=True,
    )
    tank_capacity = models.FloatField(
        verbose_name="Tank Capacity",
        null=True,
        blank=True,
    )
    length = models.FloatField(
        verbose_name="Length",
        null=True,
        blank=True
    )

    radious = models.FloatField(
        verbose_name="radious",
        null=True,
        blank=True
    )

    diameter = models.FloatField(
        verbose_name="Diameter",
        null=True,
        blank=True
    )

    difference = models.CharField(
        max_length=20,
        choices=DIFFERENCE_CHOICES,
        default='none',
        verbose_name="Difference Type",
        null=True, 
        blank=True,
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name="Is Used"
    )

    # Tracking fields
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Calibration Chart"
        verbose_name_plural = "Calibration Charts"
        ordering = ['tank_volume']

    def __str__(self):
        return f"Tank Volume {self.tank_volume}"




class CalibrationChartEntry(models.Model):
    calibration_chart = models.ForeignKey(
        CalibrationChart,
        on_delete=models.CASCADE,
        related_name="entries",
        to_field='tank_volume',
        db_column='tank_volume',
        verbose_name="Tank Volume",
        null=True,
        blank=True,
    )

    dip = models.FloatField(
        verbose_name="Dip",
        null=True,
        blank=True,
    )
    volume = models.FloatField(
        verbose_name="Volume",
        null=True,
        blank=True,
    )
    difference = models.FloatField(
        verbose_name="Difference",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Calibration Chart Entry"
        verbose_name_plural = "Calibration Chart Entries"
        ordering = ['dip']

    def __str__(self):
        return f"Dip {self.dip} - Volume {self.volume}"




class productcategory(models.Model):

    CATEGORY_TYPE_CHOICES = [
        ('category', 'Category'),
        ('type', 'Type'),
    ]
        
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPE_CHOICES,
        verbose_name="Category / Type"
    )

    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")

    # Tracking fields

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Product Category/Type"
        verbose_name_plural = "Product Categories/Types"
        ordering = ['category_type']

    def __str__(self):
        return self.category_type
    

class TankMaster(models.Model):
    tank_name = models.CharField(max_length=150, unique=True)

    # Foreign key from CalibrationChart table
    tank_volume = models.ForeignKey(
        CalibrationChart,
        on_delete=models.CASCADE,
        related_name="tanks"
    )

    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tank_master"
        ordering = ["tank_name"]
        verbose_name = "Tank Master"
        verbose_name_plural = "Tank Masters"

    def __str__(self):
        return self.tank_name
    


class GroupMaster(models.Model):

    UNDER_GROUP_CHOICES = [
        ('capital_account', 'Capital Account'),
        ('loans', 'Loans'),
        ('current_liability', 'Current Liability'),
        ('fixed_asset', 'Fixed Asset'),
        ('investments', 'Investments'),
        ('current_assets', 'Current Assets'),
        ('sales_account', 'Sales Account'),
        ('purchase_account', 'Purchase Account'),
        ('direct_income', 'Direct Income'),
        ('indirect_expense', 'Indirect Expense'),
        ('direct_expense', 'Direct Expense'),
        ('indirect_income', 'Indirect Income'),
    ]

    under_group = models.CharField(
        max_length=50,
        choices=UNDER_GROUP_CHOICES,
        verbose_name="Under Group"
    )

    group_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Group Name"
    )


    is_used = models.BooleanField(
        default=False,
        verbose_name="Is Used"
    )

    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Group Master"
        verbose_name_plural = "Group Masters"
        ordering = ['under_group', 'group_name']

    def __str__(self):
        return f"{self.group_name} ({self.get_under_group_display()})"
    




from django.utils import timezone

class LedgerMaster(models.Model):

    # DR/CR choices
    DR_CR_CHOICES = [
        ('Dr', 'Dr'),
        ('Cr', 'Cr'),
    ]

    under_group = models.ForeignKey(
        'GroupMaster',
        on_delete=models.CASCADE,
        verbose_name="Under Group"
    )

    ledger_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Ledger Name"
    )

    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        verbose_name="Opening Balance"
    )

    dr_cr = models.CharField(
        max_length=2,
        choices=DR_CR_CHOICES,
        verbose_name="Dr / Cr"
    )

    date = models.DateField(
        default=timezone.now,
        verbose_name="Date"
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name="Is Used"
    )

    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Ledger Master"
        verbose_name_plural = "Ledger Masters"
        ordering = ['ledger_name']

    def __str__(self):
        return f"{self.ledger_name} ({self.get_dr_cr_display()})"
    


class ModeOfPay(models.Model):
    bill_type_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Bill Type Name",
        null=True,
        blank=True,
    )

    # Foreign key to LedgerMaster
    ledger = models.ForeignKey(
        'LedgerMaster',
        on_delete=models.PROTECT,
        related_name="mode_of_pay_ledgers",
        verbose_name="Select Ledger",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mode_of_pay"
        ordering = ["bill_type_name"]
        verbose_name = "Mode of Pay"
        verbose_name_plural = "Modes of Pay"

    def __str__(self):
        # This ensures dropdown shows meaningful text
        return f"{self.bill_type_name} - {self.ledger.ledger_name}"
    


class TaxMaster(models.Model):
    tax_value = models.FloatField(
        max_length=150,
        unique=True,
        verbose_name="Tax Name",
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tax_master"
        ordering = ["tax_value"]
        verbose_name = "Tax Master"
        verbose_name_plural = "Tax Masters"

    def __str__(self):
        return self.tax_value
    


class VehicleType(models.Model):
    vehicle_type = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Vehicle Type",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicle_type_master"
        ordering = ["vehicle_type"]
        verbose_name = "Vehicle Type"
        verbose_name_plural = "Vehicle Types"

    def __str__(self):
        return self.vehicle_type
    



class Entry(models.Model):
    ENTRY_TYPE_CHOICES = (
        ('company', 'Company'),
        ('product', 'Product'),
    )

    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry_type.upper()} Entry"



from django.db import models
from django.utils import timezone


class Company(models.Model):
    entry = models.OneToOneField(
        'Entry',
        on_delete=models.CASCADE,
        related_name='company'
    )

    # Company Details
    company_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    # Flags
    is_supplier = models.BooleanField(default=False)
    is_used = models.BooleanField(default=True)

    # System Fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_master'
        ordering = ['company_name']

    def __str__(self):
        return self.company_name



from django.db import models
from django.utils import timezone


from django.db import models
from django.utils import timezone


class Product(models.Model):

    GST_TYPE_CHOICES = (
        ('non_tax', 'Non Tax'),
        ('inclusive', 'Inclusive'),
        ('exclusive', 'Exclusive'),
    )

    YES_NO_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )

    ST_CHOICES = (
        (12, '12%'),
        (18, '18%'),
        (20, '20%'),
        (5,  '5%'),
    )

    entry = models.OneToOneField(
        'Entry',
        on_delete=models.CASCADE,
        related_name='product',
        null=True,
        blank=True,
    )

    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
    )

    # Basic Details
    bill_code = models.CharField(max_length=50, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True, unique=True)

    pack = models.FloatField(default=0, null=True, blank=True)
    hsn_code = models.CharField(max_length=50, null=True, blank=True)

    reorder_level = models.FloatField(default=0, null=True, blank=True)

    # Product Category Mapping
    product_type = models.ForeignKey(
        'ProductCategory',
        on_delete=models.PROTECT,
        related_name='type_products',
        limit_choices_to={'category_type': 'type'},
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        'ProductCategory',
        on_delete=models.PROTECT,
        related_name='category_products',
        limit_choices_to={'category_type': 'category'},
        null=True,
        blank=True,
    )

    # GST
    sales_gst = models.CharField(
        max_length=10,
        choices=GST_TYPE_CHOICES,
        default='non_tax',
        null=True,
        blank=True
    )

    purchase_gst = models.CharField(
        max_length=10,
        choices=GST_TYPE_CHOICES,
        default='non_tax',
        null=True,
        blank=True
    )

    # NEW: ST %
    st_percent = models.PositiveSmallIntegerField(
        choices=ST_CHOICES,
        default=12,
        null=True,
        blank=True
    )

    # Tank Configuration
    tank_applicable = models.BooleanField(default=False)
    multiple_tank = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='no',
        null=True,
        blank=True,
    )

    tank = models.ForeignKey(
        'TankMaster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )

    # Stock & Rate Settings
    rate_change_fully = models.BooleanField(default=False)
    set_stock = models.BooleanField(default=False)

    initial_stock_date = models.DateField(default=timezone.now, null=True, blank=True)

    # Audit
    is_used = models.BooleanField(default=True)

    # System Fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'product_master'
        ordering = ['product_name']

    def __str__(self):
        return self.product_name or "Unnamed Product"





class ProductStock(models.Model):

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='stock_entries',
        null=True,
        blank=True
    )

    # Stock Details
    stock_qty = models.FloatField(default=0, null=True, blank=True)
    loose_qty = models.FloatField(default=0, null=True, blank=True)

    # Pricing Details
    cost_price = models.FloatField(default=0, null=True, blank=True)
    landing_cost = models.FloatField(default=0, null=True, blank=True)

    mrp = models.FloatField(default=0, null=True, blank=True)
    selling_price = models.FloatField(default=0)

    # System Fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'product_stock'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto sync landing cost and selling price
        if not self.landing_cost:
            self.landing_cost = self.cost_price

        if not self.selling_price:
            self.selling_price = self.mrp

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name if self.product else 'No Product'} | Stock: {self.stock_qty}"




class ProductTankStock(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='tank_stocks',
        verbose_name="Product"
    )

    tank = models.ForeignKey(
        'TankMaster',
        on_delete=models.PROTECT,
        related_name='product_tank_stocks',
        verbose_name="Tank Name"
    )

    stock = models.FloatField(
        verbose_name="Stock Quantity",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Product Tank Stock"
        verbose_name_plural = "Product Tank Stocks"
        ordering = ['tank__tank_name']
        unique_together = ('product', 'tank')

    def __str__(self):
        return f"{self.product.product_name} - {self.tank.tank_name} : {self.stock}"




from django.db import models


class FuelNozzleEntry(models.Model):
    ENTRY_TYPE_CHOICES = (
        ('fuel', 'Fuel'),
        ('nozzle', 'Nozzle'),
    )

    fuelnozilentry = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fuelnozilentry.upper()} Entry"



from django.db import models


class FuelEntry(models.Model):
    """
    Child table of FuelNozzleEntry (ONE-TO-ONE)
    """

    # One-to-One Parent Relation
    fuel_nozzle_entry = models.OneToOneField(
        FuelNozzleEntry,
        on_delete=models.CASCADE,
        related_name='fuel_entry'
    )

    # Tank Name (TankMaster.tank_name)
    tank = models.ForeignKey(
        TankMaster,
        on_delete=models.CASCADE,
        related_name='fuel_entries'
    )

    # Fuel Type (Product.product_name)
    fuel_type = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='fuel_entries'
    )

    # Tank Specify (CalibrationChart.tank_volume)
    tank_specify = models.ForeignKey(
        CalibrationChart,
        on_delete=models.CASCADE,
        related_name='fuel_entries'
    )

    # Status fields
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)

    # Audit fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tank.tank_name} - {self.fuel_type.product_name}"



from django.db import models


class NozzleEntry(models.Model):
    """
    Child table for Nozzle configuration
    """

    # Parent Entry (Fuel / Nozzle)
    fuel_nozzle_entry = models.OneToOneField(
        FuelNozzleEntry,
        on_delete=models.CASCADE,
        related_name='nozzle_entry'
    )

    # Tank relation (Child of TankMaster)
    tank = models.ForeignKey(
        TankMaster,
        on_delete=models.CASCADE,
        related_name='nozzle_entries'
    )

    # Nozzle Details
    nozzle_name = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    close_reading = models.FloatField()

    # Status fields
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)

    # Audit fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nozzle_name} - {self.tank.tank_name}"



from django.db import models
from django.utils import timezone


class FuelRate(models.Model):
    # Fuel Type (Select from Product.product_name)
    fuel_type = models.ForeignKey(
        'Product',                     # or Product if already imported
        on_delete=models.CASCADE,
        related_name='fuel_rates',
        verbose_name="Fuel Type"
    )

    # Fuel Rate
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Rate"
    )

    # Date & Time (default to current)
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date"
    )

    time = models.TimeField(
        default=timezone.now,
        verbose_name="Time"
    )

    # Status fields
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")

    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Fuel Rate"
        verbose_name_plural = "Fuel Rates"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.fuel_type.product_name} - {self.rate}"






from django.db import models


class Staff(models.Model):
    # =========================
    # Staff Details
    # =========================
    staff_name = models.CharField(max_length=200)
    address = models.TextField(blank=True)

    phone = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15)

    open_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    DR_CR_CHOICES = (
        ('Dr', 'Dr'),
        ('Cr', 'Cr'),
    )
    dr_cr = models.CharField(
        max_length=2,
        choices=DR_CR_CHOICES,
        default='Dr'
    )

    date = models.DateField()

    nozzle_applicable = models.BooleanField(default=False)

    # =========================
    # Flags
    # =========================
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=True)

    # =========================
    # System Fields
    # =========================
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_master'
        ordering = ['staff_name']

    def __str__(self):
        return self.staff_name
    



from django.db import models



class NozzleAllocation(models.Model):
    # =========================
    # Parent Relations
    # =========================
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='nozzle_allocations',
        null=True,
        blank=True)

    nozzle_entry = models.ForeignKey(
        NozzleEntry,
        on_delete=models.CASCADE,
        related_name='staff_allocations',
        null=True,
        blank=True
    )

    # =========================
    # Allocation Details
    # =========================
    nozzle_name = models.CharField(
        max_length=100
    )

    tank_name = models.CharField(
        max_length=100
    )

    product_name = models.CharField(
        max_length=100
    )

    # =========================
    # Flags
    # =========================
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=True)

    # =========================
    # System Fields
    # =========================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_nozzle_allocation'
        ordering = ['nozzle_name']
        unique_together = ('staff', 'nozzle_entry')

    def __str__(self):
        return f"{self.staff.staff_name} - {self.nozzle_name}"

