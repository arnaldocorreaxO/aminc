from django.urls import path

# Vistas de préstamo
from core.prestamo.views.prestamo.views import (
    TransaccionPrestamoFormView,
    Trx501, 
    Trx503, 
    Trx504
)

# Vistas de solicitud de préstamo
from core.prestamo.views.solicitud_prestamo.views import (
    SolicitudPrestamoList,
    SolicitudPrestamoCreate,
    SolicitudPrestamoUpdate,
    SolicitudPrestamoDelete,
    # AprobarSolicitudPrestamoUpdate,  # Comentado por decisión institucional
)

urlpatterns = [
    # 📄 Solicitud de Préstamo
    path("solicitud_prestamo", SolicitudPrestamoList.as_view(), name="solicitud_prestamo_list"),
    path("solicitud_prestamo/add/", SolicitudPrestamoCreate.as_view(), name="solicitud_prestamo_create"),
    path("solicitud_prestamo/update/<int:pk>/", SolicitudPrestamoUpdate.as_view(), name="solicitud_prestamo_update"),
    path("solicitud_prestamo/delete/<int:pk>/", SolicitudPrestamoDelete.as_view(), name="solicitud_prestamo_delete"),

    # Ru
    path("transaccion/", TransaccionPrestamoFormView.as_view(), name="trx_prestamo_create"), # Ruta genérica de transacción
    # 🔄 Transacciones de Préstamo
    path("trx501/", Trx501.as_view(), name="trx501_create"),
    path("trx503/", Trx503.as_view(), name="trx503_create"),
    path("trx504/", Trx504.as_view(), name="trx504_create"),
]
