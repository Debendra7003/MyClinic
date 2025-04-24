from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientProfileViewSet, PrescriptionViewSet,
    AmbulanceRequestViewSet, InsuranceViewSet
)

router = DefaultRouter()
router.register(r'profiles', PatientProfileViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'ambulance-requests', AmbulanceRequestViewSet)
router.register(r'insurances', InsuranceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]










# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import (
#     PatientProfileViewSet, MedicalHistoryViewSet, AllergyViewSet,
#     MedicationViewSet, FamilyMedicalHistoryViewSet, DocumentViewSet,
#     PatientPreferenceViewSet
# )

# router = DefaultRouter()
# router.register(r'profiles', PatientProfileViewSet)
# router.register(r'medical-history', MedicalHistoryViewSet)
# router.register(r'allergies', AllergyViewSet)
# router.register(r'medications', MedicationViewSet)
# router.register(r'family-history', FamilyMedicalHistoryViewSet)
# router.register(r'documents', DocumentViewSet)
# router.register(r'preferences', PatientPreferenceViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]