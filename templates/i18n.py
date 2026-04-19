"""
TitanForge Internationalization (i18n) Module
==============================================
Provides English/Spanish translations for the entire application.

Usage:
  - Client-side: The I18N_JS constant is injected into every page via shared_nav.py.
    It provides a global `t(key)` function and auto-translates elements with data-i18n attributes.
  - Language preference is stored in a cookie ('tf_lang') and read on page load.
  - Toggle via the sidebar settings dropdown.
"""

# ─────────────────────────────────────────────────────────────────────────────
# MASTER TRANSLATION DICTIONARY
# ─────────────────────────────────────────────────────────────────────────────
# Keys are English strings; values are Spanish translations.

TRANSLATIONS = {
    # ── Sidebar Navigation ──────────────────────
    "Dashboard": "Panel",
    "Estimating": "Estimación",
    "Calculator": "Calculadora",
    "My Projects": "Mis Proyectos",
    "Quotes": "Cotizaciones",
    "Inventory Levels": "Niveles de Inventario",
    "Projects": "Proyectos",
    "All Projects": "Todos los Proyectos",
    "Timeline": "Cronograma",
    "Budget": "Presupuesto",
    "Shop Floor": "Planta de Producción",
    "Work Orders": "Órdenes de Trabajo",
    "Workflows": "Flujos de Trabajo",
    "Machine Queues": "Colas de Máquinas",
    "Crew": "Equipo",
    "Consumable Receipts": "Recibos de Consumibles",
    "Shop Drawings": "Planos de Taller",
    "Quality": "Calidad",
    "Inspection Queue": "Cola de Inspección",
    "NCR Log": "Registro NCR",
    "AISC Library": "Biblioteca AISC",
    "Traceability": "Trazabilidad",
    "Audit Log": "Registro de Auditoría",
    "Inventory & Purchasing": "Inventario y Compras",
    "Coil Inventory": "Inventario de Bobinas",
    "Fabricated Parts": "Piezas Fabricadas",
    "Fasteners": "Tornillería",
    "Rebar Stock": "Stock de Varilla",
    "Receiving": "Recepción",
    "Allocations": "Asignaciones",
    "Mill Certs": "Certificados de Molino",
    "Purchase Orders": "Órdenes de Compra",
    "Vendors": "Proveedores",
    "Material Reqs": "Requisiciones de Material",
    "Shipping": "Envíos",
    "Build Load": "Armar Carga",
    "Active Shipments": "Envíos Activos",
    "BOL History": "Historial de Guías",
    "Field & Safety": "Campo y Seguridad",
    "Field Projects": "Proyectos de Campo",
    "Daily Reports": "Reportes Diarios",
    "Punch List": "Lista de Pendientes",
    "Photos": "Fotos",
    "Documents": "Documentos",
    "Hazard Analysis": "Análisis de Riesgos",
    "Incidents": "Incidentes",
    "Safety Metrics": "Métricas de Seguridad",
    "Training": "Capacitación",
    "Sales & Financial": "Ventas y Finanzas",
    "Sales Pipeline": "Pipeline de Ventas",
    "Leads": "Prospectos",
    "Customers": "Clientes",
    "Quote Status": "Estado de Cotización",
    "Financial Dashboard": "Panel Financiero",
    "Invoices": "Facturas",
    "Project Costs": "Costos de Proyecto",
    "Expense Reports": "Reportes de Gastos",
    "Admin & Reports": "Admin y Reportes",
    "Users": "Usuarios",
    "Settings": "Configuración",
    "Schedule": "Programación",
    "Production Reports": "Reportes de Producción",
    "Executive Summary": "Resumen Ejecutivo",
    "My Station": "Mi Estación",
    "My Machine": "Mi Máquina",
    "Run Queue": "Cola de Producción",
    "Production Log": "Registro de Producción",
    "Coil Status": "Estado de Bobina",
    "My Work": "Mi Trabajo",
    "My Queue": "Mi Cola",
    "Cut List": "Lista de Corte",
    "Completed Items": "Ítems Completados",
    "My Tasks": "Mis Tareas",
    "Tasks": "Tareas",
    "Scan": "Escanear",
    "My Project": "Mi Proyecto",
    "Project Status": "Estado del Proyecto",
    "Current Project": "Proyecto Actual",
    "Project": "Proyecto",
    "QC Dashboard": "Panel de Calidad",
    "Work Station": "Estación de Trabajo",
    "Quote Editor": "Editor de Cotización",

    # ── Sidebar UI ──────────────────────────────
    "Notifications": "Notificaciones",
    "Mark all read": "Marcar todo leído",
    "Clear All": "Limpiar Todo",
    "No notifications": "Sin notificaciones",
    "No recent notifications": "Sin notificaciones recientes",
    "Logout": "Cerrar Sesión",
    "Search projects, customers, tools...": "Buscar proyectos, clientes, herramientas...",
    "Type to search across projects, customers, and tools": "Escriba para buscar proyectos, clientes y herramientas",
    "Navigate": "Navegar",
    "Open": "Abrir",
    "Close": "Cerrar",
    "Your Profile": "Tu Perfil",
    "Language": "Idioma",
    "English": "Inglés",
    "Spanish": "Español",

    # ── Common Buttons / Actions ────────────────
    "Save": "Guardar",
    "Cancel": "Cancelar",
    "Delete": "Eliminar",
    "Edit": "Editar",
    "Add": "Agregar",
    "Create": "Crear",
    "Update": "Actualizar",
    "Submit": "Enviar",
    "Search": "Buscar",
    "Filter": "Filtrar",
    "Export": "Exportar",
    "Import": "Importar",
    "Download": "Descargar",
    "Upload": "Subir",
    "Print": "Imprimir",
    "Refresh": "Actualizar",
    "Reset": "Restablecer",
    "Back": "Atrás",
    "Next": "Siguiente",
    "Previous": "Anterior",
    "Confirm": "Confirmar",
    "Apply": "Aplicar",
    "Yes": "Sí",
    "No": "No",
    "OK": "OK",
    "Done": "Hecho",
    "Loading...": "Cargando...",
    "View": "Ver",
    "View All": "Ver Todo",
    "Show More": "Ver Más",
    "Show Less": "Ver Menos",
    "Select": "Seleccionar",
    "Select All": "Seleccionar Todo",
    "Clear": "Limpiar",
    "Copy": "Copiar",
    "Duplicate": "Duplicar",
    "Archive": "Archivar",
    "Restore": "Restaurar",
    "Approve": "Aprobar",
    "Reject": "Rechazar",
    "Send": "Enviar",
    "Close": "Cerrar",
    "Collapse": "Colapsar",
    "Expand": "Expandir",
    "Actions": "Acciones",
    "More": "Más",
    "Details": "Detalles",
    "Save Changes": "Guardar Cambios",
    "Discard Changes": "Descartar Cambios",
    "Are you sure?": "¿Está seguro?",
    "Are you sure you want to logout?": "¿Está seguro que desea cerrar sesión?",
    "Are you sure you want to delete this?": "¿Está seguro que desea eliminar esto?",
    "Successfully saved": "Guardado exitosamente",
    "Successfully deleted": "Eliminado exitosamente",
    "Successfully updated": "Actualizado exitosamente",
    "Error": "Error",
    "Success": "Éxito",
    "Warning": "Advertencia",
    "Info": "Información",
    "Required": "Requerido",
    "Optional": "Opcional",
    "None": "Ninguno",
    "N/A": "N/A",
    "All": "Todos",
    "Total": "Total",
    "Subtotal": "Subtotal",

    # ── Status Labels ───────────────────────────
    "Active": "Activo",
    "Inactive": "Inactivo",
    "Pending": "Pendiente",
    "In Progress": "En Progreso",
    "Completed": "Completado",
    "Complete": "Completo",
    "Approved": "Aprobado",
    "Rejected": "Rechazado",
    "On Hold": "En Espera",
    "Cancelled": "Cancelado",
    "Draft": "Borrador",
    "Sent": "Enviado",
    "Delivered": "Entregado",
    "Shipped": "Enviado",
    "Open": "Abierto",
    "Closed": "Cerrado",
    "Overdue": "Vencido",
    "Due Today": "Vence Hoy",
    "Scheduled": "Programado",
    "Unassigned": "Sin Asignar",
    "Assigned": "Asignado",
    "Ready": "Listo",
    "Not Started": "No Iniciado",
    "Blocked": "Bloqueado",
    "Failed": "Fallido",
    "Passed": "Aprobado",
    "Pass": "Aprobado",
    "Fail": "Reprobado",
    "New": "Nuevo",
    "Review": "Revisión",
    "Released": "Liberado",
    "Fabricating": "Fabricando",
    "Welding": "Soldando",
    "Cutting": "Cortando",
    "Drilling": "Taladrando",
    "Painting": "Pintando",
    "Loading": "Cargando",
    "In Transit": "En Tránsito",
    "Received": "Recibido",

    # ── Table / Data Headers ────────────────────
    "Name": "Nombre",
    "Date": "Fecha",
    "Created": "Creado",
    "Modified": "Modificado",
    "Created At": "Fecha de Creación",
    "Updated At": "Fecha de Actualización",
    "Description": "Descripción",
    "Status": "Estado",
    "Priority": "Prioridad",
    "Type": "Tipo",
    "Category": "Categoría",
    "Quantity": "Cantidad",
    "Qty": "Cant",
    "Unit": "Unidad",
    "Price": "Precio",
    "Cost": "Costo",
    "Amount": "Monto",
    "Weight": "Peso",
    "Length": "Longitud",
    "Width": "Ancho",
    "Height": "Altura",
    "Size": "Tamaño",
    "Thickness": "Espesor",
    "Gauge": "Calibre",
    "Color": "Color",
    "Material": "Material",
    "Notes": "Notas",
    "Comments": "Comentarios",
    "Location": "Ubicación",
    "Address": "Dirección",
    "Phone": "Teléfono",
    "Email": "Correo Electrónico",
    "Contact": "Contacto",
    "Company": "Empresa",
    "Customer": "Cliente",
    "Vendor": "Proveedor",
    "Supplier": "Proveedor",
    "Item": "Artículo",
    "Part": "Pieza",
    "Part Number": "Número de Pieza",
    "Serial Number": "Número de Serie",
    "Lot Number": "Número de Lote",
    "Batch": "Lote",
    "Order": "Orden",
    "Invoice": "Factura",
    "Quote": "Cotización",
    "PO Number": "Número de OC",
    "Job Code": "Código de Trabajo",
    "Building": "Edificio",
    "Component": "Componente",
    "Assembly": "Ensamble",

    # ── SA / TC Calculator ──────────────────────
    "SA Estimator": "Estimador SA",
    "TC Estimator": "Estimador TC",
    "Bill of Materials": "Lista de Materiales",
    "BOM": "LDM",
    "Rafter": "Viga",
    "Column": "Columna",
    "Purlin": "Larguero",
    "Sag Rod": "Tirante",
    "Brace": "Arriostramiento",
    "Girt": "Perfil Lateral",
    "Base Plate": "Placa Base",
    "Anchor Bolt": "Perno de Anclaje",
    "Ridge Cap": "Cumbrera",
    "Trim": "Moldura",
    "Panel": "Panel",
    "Eave": "Alero",
    "Peak": "Cumbrera",
    "Bay": "Tramo",
    "Span": "Claro",
    "Slope": "Pendiente",
    "Pitch": "Pendiente",
    "Width": "Ancho",
    "Length": "Largo",
    "Eave Height": "Altura de Alero",
    "Number of Bays": "Número de Tramos",
    "Bay Spacing": "Espaciamiento de Tramos",
    "Wind Speed": "Velocidad del Viento",
    "Snow Load": "Carga de Nieve",
    "Roof Panel": "Panel de Techo",
    "Wall Panel": "Panel de Pared",
    "Endwall": "Muro Testero",
    "Sidewall": "Muro Lateral",
    "Frame Type": "Tipo de Marco",
    "Clear Span": "Claro Libre",
    "Multi-Span": "Multi-Claro",
    "Lean-To": "Adosado",
    "Generate BOM": "Generar LDM",
    "Save Project": "Guardar Proyecto",
    "Load Project": "Cargar Proyecto",
    "New Project": "Nuevo Proyecto",
    "Project Name": "Nombre del Proyecto",
    "Customer Name": "Nombre del Cliente",
    "Job Number": "Número de Trabajo",

    # ── Work Orders ─────────────────────────────
    "Work Order": "Orden de Trabajo",
    "Work Order #": "Orden de Trabajo #",
    "Create Work Order": "Crear Orden de Trabajo",
    "Assign To": "Asignar A",
    "Due Date": "Fecha de Entrega",
    "Start Date": "Fecha de Inicio",
    "End Date": "Fecha de Fin",
    "Estimated Hours": "Horas Estimadas",
    "Actual Hours": "Horas Reales",
    "Progress": "Progreso",
    "Line Items": "Líneas de Artículos",
    "Add Item": "Agregar Artículo",
    "Remove Item": "Eliminar Artículo",
    "Mark Complete": "Marcar Completo",
    "Reopen": "Reabrir",

    # ── QC / Quality ────────────────────────────
    "Inspection": "Inspección",
    "Inspector": "Inspector",
    "Inspection Date": "Fecha de Inspección",
    "Finding": "Hallazgo",
    "Corrective Action": "Acción Correctiva",
    "Non-Conformance": "No Conformidad",
    "NCR": "RNC",
    "Hold Point": "Punto de Espera",
    "Release": "Liberar",
    "Disposition": "Disposición",
    "Root Cause": "Causa Raíz",
    "Severity": "Severidad",
    "Minor": "Menor",
    "Major": "Mayor",
    "Critical": "Crítico",
    "Calibration": "Calibración",
    "Certificate": "Certificado",
    "Specification": "Especificación",
    "Tolerance": "Tolerancia",
    "Measured Value": "Valor Medido",
    "Acceptance Criteria": "Criterio de Aceptación",
    "Test Report": "Reporte de Prueba",

    # ── Inventory / Purchasing ──────────────────
    "In Stock": "En Stock",
    "Out of Stock": "Agotado",
    "Low Stock": "Stock Bajo",
    "Reorder Point": "Punto de Reorden",
    "Minimum Stock": "Stock Mínimo",
    "On Order": "En Pedido",
    "Available": "Disponible",
    "Reserved": "Reservado",
    "Allocated": "Asignado",
    "Consumed": "Consumido",
    "Coil": "Bobina",
    "Coil ID": "ID de Bobina",
    "Heat Number": "Número de Colada",
    "Gauge": "Calibre",
    "Width": "Ancho",
    "Weight (lbs)": "Peso (lbs)",
    "Footage": "Metraje",
    "Remaining": "Restante",
    "Add Coil": "Agregar Bobina",
    "Edit Coil": "Editar Bobina",
    "Delete Coil": "Eliminar Bobina",
    "Vendor": "Proveedor",
    "Unit Price": "Precio Unitario",
    "Total Cost": "Costo Total",
    "Lead Time": "Tiempo de Entrega",
    "Payment Terms": "Términos de Pago",
    "Ship Via": "Enviar Vía",
    "FOB": "LAB",

    # ── Shipping ────────────────────────────────
    "Bill of Lading": "Guía de Embarque",
    "BOL": "Guía",
    "Carrier": "Transportista",
    "Truck Number": "Número de Camión",
    "Driver": "Conductor",
    "Pickup Date": "Fecha de Recogida",
    "Delivery Date": "Fecha de Entrega",
    "Destination": "Destino",
    "Load": "Carga",
    "Unload": "Descarga",
    "Shipment": "Envío",
    "Tracking Number": "Número de Rastreo",
    "Pieces": "Piezas",
    "Bundles": "Paquetes",
    "Skids": "Tarimas",

    # ── Field & Safety ──────────────────────────
    "Job Site": "Sitio de Trabajo",
    "Foreman": "Capataz",
    "Superintendent": "Superintendente",
    "Weather": "Clima",
    "Temperature": "Temperatura",
    "Crew Size": "Tamaño del Equipo",
    "Hours Worked": "Horas Trabajadas",
    "Safety": "Seguridad",
    "Incident": "Incidente",
    "Incident Report": "Reporte de Incidente",
    "Near Miss": "Casi Accidente",
    "Injury": "Lesión",
    "First Aid": "Primeros Auxilios",
    "Recordable": "Registrable",
    "Lost Time": "Tiempo Perdido",
    "Job Hazard Analysis": "Análisis de Riesgos del Trabajo",
    "JHA": "ART",
    "PPE": "EPP",
    "Toolbox Talk": "Charla de Seguridad",
    "Daily Report": "Reporte Diario",
    "Punch Item": "Pendiente",
    "Photo": "Foto",
    "Take Photo": "Tomar Foto",
    "Upload Photo": "Subir Foto",
    "Complete": "Completo",
    "Incomplete": "Incompleto",

    # ── Financial / Sales ───────────────────────
    "Revenue": "Ingresos",
    "Profit": "Ganancia",
    "Margin": "Margen",
    "Discount": "Descuento",
    "Tax": "Impuesto",
    "Subtotal": "Subtotal",
    "Grand Total": "Gran Total",
    "Payment": "Pago",
    "Paid": "Pagado",
    "Unpaid": "No Pagado",
    "Partial": "Parcial",
    "Balance Due": "Saldo Pendiente",
    "Due Amount": "Monto Adeudado",
    "Invoice Date": "Fecha de Factura",
    "Payment Date": "Fecha de Pago",
    "Terms": "Términos",
    "Net 30": "Neto 30",
    "Net 60": "Neto 60",
    "COD": "Contra Entrega",
    "Lead": "Prospecto",
    "Prospect": "Prospecto",
    "Opportunity": "Oportunidad",
    "Won": "Ganado",
    "Lost": "Perdido",
    "Proposal": "Propuesta",
    "Contract": "Contrato",

    # ── Profile Page ────────────────────────────
    "My Profile": "Mi Perfil",
    "Account Information": "Información de Cuenta",
    "Display Name": "Nombre para Mostrar",
    "Change Password": "Cambiar Contraseña",
    "Current Password": "Contraseña Actual",
    "New Password": "Nueva Contraseña",
    "Confirm Password": "Confirmar Contraseña",
    "Update Password": "Actualizar Contraseña",
    "Save Preferences": "Guardar Preferencias",
    "Notification Preferences": "Preferencias de Notificaciones",
    "Work Order Updates": "Actualizaciones de Órdenes de Trabajo",
    "Get notified when work orders are created or status changes": "Recibir notificaciones cuando se crean órdenes o cambia el estado",
    "QC Inspections": "Inspecciones de Calidad",
    "Alerts for inspection results and NCRs": "Alertas de resultados de inspección y RNCs",
    "Shipping Updates": "Actualizaciones de Envío",
    "Notifications when loads are built or shipped": "Notificaciones cuando se arman o envían cargas",
    "Inventory Alerts": "Alertas de Inventario",
    "Low stock warnings and receiving notifications": "Avisos de stock bajo y notificaciones de recepción",
    "Safety Incidents": "Incidentes de Seguridad",
    "Immediate alerts for safety incidents and near misses": "Alertas inmediatas de incidentes de seguridad y casi accidentes",

    # ── Admin / Reports ─────────────────────────
    "User Management": "Gestión de Usuarios",
    "Role": "Rol",
    "Permissions": "Permisos",
    "Last Login": "Último Inicio de Sesión",
    "Account": "Cuenta",
    "Password": "Contraseña",
    "Username": "Nombre de Usuario",
    "Full Name": "Nombre Completo",
    "Report": "Reporte",
    "Reports": "Reportes",
    "Generate Report": "Generar Reporte",
    "Date Range": "Rango de Fechas",
    "From": "Desde",
    "To": "Hasta",
    "Today": "Hoy",
    "This Week": "Esta Semana",
    "This Month": "Este Mes",
    "This Year": "Este Año",
    "Last 7 Days": "Últimos 7 Días",
    "Last 30 Days": "Últimos 30 Días",
    "Custom Range": "Rango Personalizado",
    "Summary": "Resumen",
    "Chart": "Gráfica",
    "Table": "Tabla",
    "Export PDF": "Exportar PDF",
    "Export Excel": "Exportar Excel",
    "Export CSV": "Exportar CSV",

    # ── Login / Auth ────────────────────────────
    "Sign In": "Iniciar Sesión",
    "Sign Out": "Cerrar Sesión",
    "Login": "Iniciar Sesión",
    "Log In": "Iniciar Sesión",
    "Register": "Registrarse",
    "Forgot Password": "Olvidé mi Contraseña",
    "Reset Password": "Restablecer Contraseña",
    "Remember Me": "Recordarme",
    "Welcome": "Bienvenido",
    "Welcome back": "Bienvenido de nuevo",

    # ── Dashboard Widgets ───────────────────────
    "Active Projects": "Proyectos Activos",
    "Open Work Orders": "Órdenes de Trabajo Abiertas",
    "Pending Inspections": "Inspecciones Pendientes",
    "Overdue Items": "Ítems Vencidos",
    "Recent Activity": "Actividad Reciente",
    "Quick Actions": "Acciones Rápidas",
    "Performance": "Rendimiento",
    "Efficiency": "Eficiencia",
    "On Time": "A Tiempo",
    "Utilization": "Utilización",
    "Throughput": "Rendimiento",
    "Capacity": "Capacidad",
    "Backlog": "Atraso",
    "This Week": "Esta Semana",
    "vs Last Week": "vs Semana Pasada",

    # ── Time / Date ─────────────────────────────
    "just now": "ahora mismo",
    "ago": "hace",
    "minute": "minuto",
    "minutes": "minutos",
    "hour": "hora",
    "hours": "horas",
    "day": "día",
    "days": "días",
    "week": "semana",
    "weeks": "semanas",
    "month": "mes",
    "months": "meses",
    "year": "año",
    "years": "años",
    "Yesterday": "Ayer",
    "Tomorrow": "Mañana",

    # ── Misc / Common Page Text ─────────────────
    "No data available": "Sin datos disponibles",
    "No results found": "Sin resultados",
    "No items": "Sin artículos",
    "No records found": "Sin registros",
    "Coming Soon": "Próximamente",
    "Under Construction": "En Construcción",
    "Page not found": "Página no encontrada",
    "Access Denied": "Acceso Denegado",
    "Unauthorized": "No Autorizado",
    "Something went wrong": "Algo salió mal",
    "Please try again": "Por favor intente de nuevo",
    "Select a project": "Seleccione un proyecto",
    "Select a customer": "Seleccione un cliente",
    "Enter": "Ingresar",
    "Choose": "Elegir",
    "Showing": "Mostrando",
    "of": "de",
    "results": "resultados",
    "rows": "filas",
    "per page": "por página",
    "Page": "Página",
    "First": "Primero",
    "Last": "Último",
    "Sort by": "Ordenar por",
    "Group by": "Agrupar por",
    "Ascending": "Ascendente",
    "Descending": "Descendente",

    # ── Form Labels ─────────────────────────────
    "First Name": "Nombre",
    "Last Name": "Apellido",
    "City": "Ciudad",
    "State": "Estado",
    "Zip Code": "Código Postal",
    "Country": "País",
    "Fax": "Fax",
    "Website": "Sitio Web",
    "Tax ID": "RFC",
    "Account Number": "Número de Cuenta",
    "Routing Number": "Número de Ruta",
    "Bank Name": "Nombre del Banco",

    # ── Confirmation Dialogs ────────────────────
    "Confirm Delete": "Confirmar Eliminación",
    "This action cannot be undone.": "Esta acción no se puede deshacer.",
    "Are you sure you want to delete this item?": "¿Está seguro que desea eliminar este artículo?",
    "Delete selected items?": "¿Eliminar artículos seleccionados?",
    "Unsaved changes will be lost.": "Los cambios no guardados se perderán.",
    "Save before leaving?": "¿Guardar antes de salir?",

    # ── Gamification / XP ───────────────────────
    "Level": "Nivel",
    "XP": "XP",
    "Achievements": "Logros",
    "Leaderboard": "Tabla de Líderes",
    "Streak": "Racha",
    "Points": "Puntos",
    "Rank": "Rango",
    "Badge": "Insignia",
    "Unlocked": "Desbloqueado",
    "Locked": "Bloqueado",

    # ── Print / PDF ─────────────────────────────
    "Print Preview": "Vista Previa de Impresión",
    "Save as PDF": "Guardar como PDF",
    "Save PDF to Project": "Guardar PDF al Proyecto",
    "Download PDF": "Descargar PDF",
    "Page Setup": "Configurar Página",
    "Landscape": "Horizontal",
    "Portrait": "Vertical",
    "Paper Size": "Tamaño de Papel",

    # ── Shop Drawing Specifics ──────────────────
    "Interactive Drawing": "Plano Interactivo",
    "Reset Zoom": "Restablecer Zoom",
    "Zoom In": "Acercar",
    "Zoom Out": "Alejar",
    "Pan": "Mover",
    "Rotate": "Rotar",
    "Title Block": "Cuadro de Título",
    "Scale": "Escala",
    "Revision": "Revisión",
    "Date Drawn": "Fecha de Dibujo",
    "Drawn By": "Dibujado Por",
    "Checked By": "Revisado Por",
    "Approved By": "Aprobado Por",
    "Sheet": "Hoja",
    "of": "de",
}


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT-SIDE JS — injected into every page
# ─────────────────────────────────────────────────────────────────────────────

def build_i18n_js():
    """Build the JS translation system injected into every page."""
    import json
    translations_json = json.dumps(TRANSLATIONS, ensure_ascii=False)

    return r"""
// ── TitanForge i18n System ──────────────────────
(function() {
    'use strict';

    var _translations = """ + translations_json + r""";

    // Read language from cookie
    function getLang() {
        var m = document.cookie.match(/(?:^|;\s*)tf_lang=([^;]+)/);
        return m ? m[1] : 'en';
    }

    // Set language cookie (365 days)
    function setLang(lang) {
        document.cookie = 'tf_lang=' + lang + ';path=/;max-age=31536000;SameSite=Lax';
    }

    // Translate a string
    function t(key) {
        if (getLang() === 'es' && _translations[key]) {
            return _translations[key];
        }
        return key;
    }

    // Translate time-ago strings
    function tTime(str) {
        if (getLang() !== 'es') return str;
        return str
            .replace(/^just now$/, 'ahora mismo')
            .replace(/(\d+)m ago/, '$1m atrás')
            .replace(/(\d+)h ago/, '$1h atrás')
            .replace(/(\d+)d ago/, '$1d atrás');
    }

    // Auto-translate all elements with data-i18n attribute
    function translatePage() {
        if (getLang() !== 'es') return;

        // Translate data-i18n elements
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            if (_translations[key]) {
                el.textContent = _translations[key];
            }
        });

        // Translate data-i18n-placeholder elements
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
            var key = el.getAttribute('data-i18n-placeholder');
            if (_translations[key]) {
                el.placeholder = _translations[key];
            }
        });

        // Translate data-i18n-title elements
        document.querySelectorAll('[data-i18n-title]').forEach(function(el) {
            var key = el.getAttribute('data-i18n-title');
            if (_translations[key]) {
                el.title = _translations[key];
            }
        });

        // Smart text-node translation: walk through visible text nodes
        // and translate known English strings
        translateTextNodes(document.body);
    }

    // Walk text nodes and translate known strings
    function translateTextNodes(root) {
        if (!root) return;
        var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
        var node;
        while (node = walker.nextNode()) {
            var text = node.nodeValue;
            if (!text || !text.trim()) continue;
            // Skip script/style tags
            var parent = node.parentNode;
            if (!parent) continue;
            var tag = parent.tagName;
            if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA' || tag === 'CODE' || tag === 'PRE') continue;
            // Skip input values and editable content
            if (parent.isContentEditable) continue;

            var trimmed = text.trim();

            // Direct match
            if (_translations[trimmed]) {
                node.nodeValue = text.replace(trimmed, _translations[trimmed]);
                continue;
            }

            // Partial matches for common patterns
            var changed = text;
            // Handle "X items", "Showing X of Y" etc.
            changed = changed.replace(/\bLoading\.\.\./g, 'Cargando...');
            changed = changed.replace(/\bNo data available\b/g, 'Sin datos disponibles');
            changed = changed.replace(/\bNo results found\b/g, 'Sin resultados');
            changed = changed.replace(/\bNo records found\b/g, 'Sin registros');
            changed = changed.replace(/\bComing Soon\b/g, 'Próximamente');
            changed = changed.replace(/\bPage not found\b/g, 'Página no encontrada');
            changed = changed.replace(/\bjust now\b/g, 'ahora mismo');

            if (changed !== text) {
                node.nodeValue = changed;
            }
        }
    }

    // Toggle language
    function toggleLanguage() {
        var current = getLang();
        var newLang = current === 'en' ? 'es' : 'en';
        setLang(newLang);
        // Reload to apply translations everywhere
        window.location.reload();
    }

    // Expose globally
    window.tfI18n = {
        t: t,
        tTime: tTime,
        getLang: getLang,
        setLang: setLang,
        translatePage: translatePage,
        toggleLanguage: toggleLanguage,
        translations: _translations
    };
    window.t = t;

    // Auto-translate on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', translatePage);
    } else {
        translatePage();
    }

    // Re-translate after any AJAX content loads (MutationObserver)
    var _translateTimer = null;
    var observer = new MutationObserver(function(mutations) {
        // Debounce: translate 200ms after last DOM mutation
        clearTimeout(_translateTimer);
        _translateTimer = setTimeout(function() {
            if (getLang() === 'es') {
                // Only translate newly added nodes
                mutations.forEach(function(m) {
                    m.addedNodes.forEach(function(n) {
                        if (n.nodeType === 1) {
                            // Translate data-i18n in new nodes
                            n.querySelectorAll && n.querySelectorAll('[data-i18n]').forEach(function(el) {
                                var key = el.getAttribute('data-i18n');
                                if (_translations[key]) el.textContent = _translations[key];
                            });
                            translateTextNodes(n);
                        }
                    });
                });
            }
        }, 200);
    });
    observer.observe(document.body || document.documentElement, { childList: true, subtree: true });
})();
"""


# Pre-build the JS string at import time
I18N_JS = build_i18n_js()
