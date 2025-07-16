from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import CostingConfigSerializer
from rest_framework.response import Response
from MyClinic.permissions import IsAdmin
from .models import CostingConfig
from Labs.models import LabTest
from DoctorAccess.models import DoctorAppointment
from LoginAccess.models import User
from datetime import datetime, date


def calculate_fixed_income(config, start_date, end_date):
    if not config.fixed_amount:
        return 0

    # Fallback to config-defined period
    start = start_date or config.effective_from
    end = end_date or config.effective_to or date.today()
    print("1st: ", start, "-----", end)

    # Parse strings if needed
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d").date()
        print("2nd", start)
    if isinstance(end, str):
        end = datetime.strptime(end, "%Y-%m-%d").date()
        print("3rd", end)

    if end < start:
        return 0  # Invalid period

    delta_days = (end - start).days + 1
    print("4th", delta_days)
    if config.period == 'monthly':
        months = (end.year - start.year) * 12 + (end.month - start.month) + 1
        print("5th", months)
        return config.fixed_amount * months

    elif config.period == 'weekly':
        weeks = delta_days // 7
        if delta_days % 7 != 0:
            weeks += 1
        print("6th", weeks)
        return config.fixed_amount * weeks

    elif config.period == 'yearly':
        years = end.year - start.year
        if (end.month, end.day) >= (start.month, start.day):
            years += 1
        print("7th", years)
        return config.fixed_amount * years

    return config.fixed_amount

class AdminCostingAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        entity_type = request.GET.get('entity_type')  # 'doctor' or 'lab'
        entity_id = request.GET.get('entity_id')      # user_id of doctor/lab
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        filters = {}
        if entity_type:
            filters['entity_type'] = entity_type
        if entity_id:
            filters['entity__user_id'] = entity_id
        # if start_date:
        #     filters['effective_from__lte'] = start_date
        # if end_date:
        #     filters['effective_to__gte'] = end_date

        configs = CostingConfig.objects.filter(**filters)

        results = []
        for config in configs:
            if config.entity_type == 'doctor':
                appointment_filters = {'doctor_id': config.entity,
                                       'cancelled': False,
                                       'checked': True}
                # if start_date:
                #     appointment_filters['date_of_visit__gte'] = start_date
                # if end_date:
                #     appointment_filters['date_of_visit__lte'] = end_date
                
                period_start = max(datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else config.effective_from,
                                   config.effective_from
                                   )
                period_end = min(
                    datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else (config.effective_to or date.today()),
                    config.effective_to or date.today()
                )

                appointment_filters['date_of_visit__gte'] = period_start
                appointment_filters['date_of_visit__lte'] = period_end

                appointments = DoctorAppointment.objects.filter(**appointment_filters)

                # appointments = DoctorAppointment.objects.filter(
                #     doctor_id=config.entity,
                #     date_of_visit__gte=start_date,
                #     date_of_visit__lte=end_date,
                #     cancelled=False,
                #     checked=True  # May be a problem if doctor dont click checked.(To hide from admin)
                # )

                count = appointments.count()
                if config.costing_type == 'per_patient':
                    admin_income = (config.per_patient_amount or 0) * count
                elif config.costing_type == 'fixed':
                    # admin_income = config.fixed_amount or 0
                    admin_income = calculate_fixed_income(config, start_date, end_date)
                else:
                    admin_income = 0
                results.append({
                    "entity_type": "doctor",
                    "entity_id": config.entity.user_id,
                    # "entity_name": config.entity.get_full_name(),
                    "entity_name": f"{config.entity.first_name} {config.entity.last_name}".strip(),
                    "costing_type": config.costing_type,
                    "per_patient_amount": str(config.per_patient_amount),
                    "fixed_amount": str(config.fixed_amount),
                    "period": config.period,
                    "effective_from": config.effective_from,
                    "effective_to": config.effective_to,
                    "total_appointments": count,
                    "admin_income": str(admin_income),
                    "notes": config.notes,
                })
            elif config.entity_type == 'lab':
                lab_filters = {'lab_profile__user': config.entity,
                               'status': 'COMPLETED'}
                # if start_date:
                #     lab_filters['scheduled_date__gte'] = start_date
                # if end_date:
                #     lab_filters['scheduled_date__lte'] = end_date

                period_start = max(datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else config.effective_from,
                                   config.effective_from
                                   )
                period_end = min(datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else (config.effective_to or date.today()),
                                    config.effective_to or date.today()
                                    )

                lab_filters['scheduled_date__gte'] = period_start
                lab_filters['scheduled_date__lte'] = period_end

                lab_tests = LabTest.objects.filter(**lab_filters)

                # lab_tests = LabTest.objects.filter(
                #     lab_profile__user=config.entity,
                #     scheduled_date__gte=start_date,
                #     scheduled_date__lte=end_date,
                #     status='COMPLETED'
                # )
                count = lab_tests.count()
                if config.costing_type == 'per_patient':
                    admin_income = (config.per_patient_amount or 0) * count
                elif config.costing_type == 'fixed':
                    # admin_income = config.fixed_amount or 0
                    admin_income = calculate_fixed_income(config, start_date, end_date)
                else:
                    admin_income = 0
                results.append({
                    "entity_type": "lab",
                    "entity_id": config.entity.user_id,
                    # "entity_name": config.entity.get_full_name(),
                    "entity_name": f"{config.entity.first_name} {config.entity.last_name}".strip(),
                    "costing_type": config.costing_type,
                    "per_patient_amount": str(config.per_patient_amount),
                    "fixed_amount": str(config.fixed_amount),
                    "period": config.period,
                    "effective_from": config.effective_from,
                    "effective_to": config.effective_to,
                    "total_lab_tests": count,
                    "admin_income": str(admin_income),
                    "notes": config.notes,
                })
        return Response(results)
    

class CostingConfigViewSet(viewsets.ModelViewSet):
    queryset = CostingConfig.objects.all()
    serializer_class = CostingConfigSerializer
    permission_classes = [IsAdmin]