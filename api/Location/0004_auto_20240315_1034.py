from django.db import migrations
from api.models import District, State, Location

def populate_districts(apps, schema_editor):
    kerala = State.objects.get(name='Kerala')
    
    # Add locations for Ernakulam district
    ernakulam = District.objects.get(name='Ernakulam', state=kerala)
    ernakulam_locations = ['Kakkanad', 'Kaloor', 'Edappaly', 'Aluva', 'JNL', 'Fort Kochi']
    for location_name in ernakulam_locations:
        Location.objects.create(name=location_name, district=ernakulam)
    
    # Add locations for Thrissur district
    thrissur = District.objects.get(name='Thrissur', state=kerala)
    thrissur_locations = ['Chalakudy', 'Guruvayur', 'Irinjalakuda', 'Wadakkancherry']
    for location_name in thrissur_locations:
        Location.objects.create(name=location_name, district=thrissur)

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20240314_1629'),
    ]

    operations = [
        migrations.RunPython(populate_districts),
    ]
