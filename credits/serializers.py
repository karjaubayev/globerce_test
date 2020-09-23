from rest_framework import serializers
from credits.models import Person, Program, CreditRequest

class CreditRequestSerializer(serializers.ModelSerializer):
    iin = serializers.CharField(source='person')
    sum = serializers.IntegerField(min_value=0)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CreditRequest
        fields = ('iin', 'sum', 'status', 'decline')
        extra_kwargs = {
            'status': {'required': False},
            'decline': {'required': False}
        }
    
    def create(self, validated_data):
        person, created = Person.objects.get_or_create(iin=validated_data['person'])
        # person = Person.objects.create(iin=validated_data['person'])
        program = Program.objects.last()
        obj = CreditRequest.objects.create(program=program, person=person, sum=validated_data['sum'])
        return obj