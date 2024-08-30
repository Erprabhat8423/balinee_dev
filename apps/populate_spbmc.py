from apps.src.models.models import SpBMC,SpMPP, SpUsers  # Replace `myapp` with the actual app name
from datetime import datetime

# bmc_data = [
#     {"name": "BMC 1", "bmc_code": "BMC001", "employee_id": 109},
#     {"name": "BMC 2", "bmc_code": "BMC002", "employee_id": 109},
#     {"name": "BMC 3", "bmc_code": "BMC003", "employee_id": 109},
#     {"name": "BMC 4", "bmc_code": "BMC004", "employee_id": 109},
#     {"name": "BMC 5", "bmc_code": "BMC005", "employee_id": 109},
#     {"name": "BMC 6", "bmc_code": "BMC006", "employee_id": 109},
#     {"name": "BMC 7", "bmc_code": "BMC007", "employee_id": 109},
#     {"name": "BMC 8", "bmc_code": "BMC008", "employee_id": 109},
#     {"name": "BMC 9", "bmc_code": "BMC009", "employee_id": 109},
#     {"name": "BMC 10", "bmc_code": "BMC010", "employee_id": 109},
# ]

# def populate_spbmc():
#     for data in bmc_data:
#         try:
#             employee = SpUsers.objects.get(id=data['employee_id'])
#         except SpUsers.DoesNotExist:
#             print(f"User with ID {data['employee_id']} does not exist. Skipping.")
#             continue
        
#         SpBMC.objects.create(
#             name=data['name'],
#             bmc_code=data['bmc_code'],
#             emplyee=employee,
#             status=1,
#             created_at=datetime.now(),
#             updated_at=datetime.now(),
#         )
    
#     print("SpBMC table populated with 10 records successfully!")

# populate_spbmc()
import random
from django.core.management.base import BaseCommand

def populate_mpp_for_bmc():
    # Fetch the BMC records related to employee_id 109
    bmc_records = SpBMC.objects.filter(emplyee_id=109)
    mpp_data = []
    for bmc in bmc_records:
        num_mpp_records = random.randint(2, 5)  # Generate between 2 and 5 records for each BMC
        for i in range(num_mpp_records):
            mpp_data.append(SpMPP(
                name=f"MPP Name {i+1} for BMC {bmc.name}",
                mpp_code=f"MPP_{i+1}_{bmc.bmc_code}",
                bmc=bmc,
                latitude=f"{random.uniform(20.0, 30.0):.6f}",
                longitude=f"{random.uniform(70.0, 80.0):.6f}",
                status=random.choice([0, 1])
            ))

    # Bulk create MPP records
    SpMPP.objects.bulk_create(mpp_data)
    print("SpBMC table populated with 10 records successfully!")
    
populate_mpp_for_bmc()