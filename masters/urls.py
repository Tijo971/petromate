from django.urls import path
from .views import*



app_name = 'masters'

urlpatterns = [
    path('dashboard/', baseview.as_view(), name='dashboard'),
    path('productcategory/', productcategoryview.as_view(), name='productcategory'),
    # Delete a product category
    path('productcategory/delete/<int:pk>/', delete_package_type, name='delete_productcategory'),
    # Export product categories (excel or pdf)
    path('productcategory/export/<str:export_type>/', export_package_types, name='export_productcategory'),
    path('tankmaster/', tankmasterview.as_view(), name='tankmaster'),

    # Delete
    path('tankmaster/delete/<int:pk>/', delete_tank, name='delete_tank'),

    # Export
    path('tankmaster/export/<str:export_type>/', export_tanks, name='export_tanks'),
        path('fuel-rate/', FuelRateView.as_view(), name='fuel_rate'),
        path('fuel-rate/export/<str:export_type>/', export_fuel_rates, name='export_fuel_rates'),
        path('fuel-rate/delete/<int:pk>/', delete_fuel_rate, name='delete_fuel_rate'),

    path("nozzle-staff-alloc/", NozzleStaffAllocView.as_view(), name="nozzle_staff_alloc"),
    path('entry/create/', EntryMasterView.as_view(), name='entry_master'),
    path('entry/delete/<int:pk>/', EntryDeleteView.as_view(), name='entry_delete'),
    path('product-delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'), 
    path('entries/export/<str:export_type>/',export_companies, name='export_companies'),
    path(
        'tank/delete/<int:pk>/',
        ProductStockDeleteView.as_view(),
        name='tank_delete'
    ),
        path(
        'export/products/<str:export_type>/',
        export_products,
        name='export_products'
    ),

       path(
        'fuel-nozzle/',
        FuelNozzleMasterView.as_view(),
        name='fuel_nozzle_master'
    ),

     path('delete-fuel-entry/<int:pk>/', FuelEntryDeleteView.as_view(), name='delete_fuel_entry'),


    path(
    'delete-fuel-nozzle/<int:pk>/',
    FuelNozzleDeleteView.as_view(),
    name='delete_fuel_nozzle'
    ),


    # urls.py
path(
    'tank-details/<int:tank_id>/',
    get_tank_details,
    name='get_tank_details'
),

    path(
        'fuel-entry-report/<str:export_type>/',
        export_fuel_entries,
        name='fuel_entry_report'
    ),


        path(
        'nozzle-fuel-report/<str:export_type>/',
        export_nozzle_fuel_entries,
        name='nozzle_fuel_report'
    ),









        # Vehicle Type Master
    path(
        'vehicle-type/',
        VehicleTypeMasterView.as_view(),
        name='vehicle_type_master'
    ),

    # Delete Vehicle Type
    path(
        'vehicle-type/delete/<int:pk>/',
        delete_vehicle_type,
        name='delete_vehicle_type'
    ),

    # Export Vehicle Type (excel / pdf)
    path(
        'vehicle-type/export/<str:export_type>/',
        export_vehicle_type_master,
        name='export_vehicle_type_master'
    ),
    path('managecustomerview/', managecustomerview.as_view(), name='managecustomerview'),
    path('indentissueview', indentissueview.as_view(), name='indentissueview'),
    path('customeroutstandingview/', customeroutstandingview.as_view(), name='customeroutstandingview'),
    path('managesupplierview/', managesupplierview.as_view(), name='managesupplierview'),
    path('supplieroutstandingview/', supplieroutstandingview.as_view(), name='supplieroutstandingview'),
    path(
        'staff/',
        StaffMasterView.as_view(),
        name='staffmaster'
    ),
    path('staff/delete/<int:pk>/', delete_staff, name='delete_staff'),

    path('staffs/export/<str:export_type>/',export_staff_list, name='export_staff'),


    # calibration chart urls
    # List + Create + Update
    path(
        'calibration-chart/',
        CalibrationChartView.as_view(),
        name='calibrationchart'
    ),

    # Delete
    path(
        'calibration-chart/delete/<int:pk>/',
        delete_calibration_chart,
        name='delete_calibrationchart'
    ),

    # Export (Excel)
path(
    'calibration-chart/export/<str:export_type>/',
    export_calibration_chart,
    name='export_calibration_chart'
),

    # urls.py
path(
    "ajax/get-dip-by-tank/",
    get_dip_by_tank_volume,
    name="get_dip_by_tank_volume"
),

path(
    'calibration-chart/<int:chart_id>/export/<str:export_type>/',
    export_dip_entries,
    name='export_dip_entries'
),




    path('densitychartview/', densitychartview.as_view(), name='densitychartview'),
    path('resetshiftview/', resetshiftview.as_view(), name='resetshiftview'),
    path('deleteshiftview/', deleteshiftview.as_view(), name='deleteshiftview'),
     path('groupmaster/', GroupMasterView.as_view(), name='groupmaster'),

    # Delete Group
    path('groupmaster/delete/<int:pk>/', delete_group_master, name='delete_groupmaster'),

    # Export Group Master
    path('groupmaster/export/<str:export_type>/', export_group_master, name='export_groupmaster'),
    path('ledgermaster/', LedgerMasterView.as_view(), name='ledgermaster'),

    # Delete ledger
    path('ledger/delete/<int:pk>/',delete_ledger_master,name='delete_ledger_master'),

    # Export ledger (excel/pdf)
    path('ledgermaster/export/<str:export_type>/', export_ledger_master, name='export_ledgermaster'),
    path('bankdetailsview/', bankdetailsview.as_view(), name='bankdetailsview'),
        # ================= MODE OF PAY =================
    path(
        'mode-of-pay/',
        ModeOfPayView.as_view(),
        name='modeofpay'
    ),

    path(
        'mode-of-pay/delete/<int:pk>/',
        delete_mode_of_pay,
        name='delete_modeofpay'
    ),

    path(
        'mode-of-pay/export/<str:export_type>/',
        export_mode_of_pay,
        name='export_modeofpay'
    ),
        # Tax Master list, add, edit
    path('tax-master/', TaxMasterView.as_view(), name='taxmaster'),

    # Delete Tax Master
    path('tax-master/delete/<int:pk>/', delete_tax_master, name='delete_taxmaster'),

    # Export Tax Master (excel/pdf)
    path('tax-master/export/<str:export_type>/', export_tax_master, name='export_taxmaster'),
    path('stockadjustmentview/', stockadjustmentview.as_view(), name='stockadjustmentview'),

]