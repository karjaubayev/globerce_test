from django.db import models
from datetime import datetime, date
import requests, json

class ValidateRequest():
    
    def __init__(self, program, person, sum):
        self.program = program
        self.person = person
        self.sum = sum
    
    def __str__(self):
        return f"{self.program}-{self.person}-{self.sum}"
    
    @property
    def status(self):
        if (self.program.check_sum(sum=self.sum) and 
            self.program.check_age(age=self.person.age) and 
            self.person.not_ip() and 
            self.person.not_banned()):
            
            return True
        else:
            return False
    
    @property
    def text(self):
        text = ""
        if not self.program.check_sum(sum=self.sum):
            text += "Заявка не подходит по сумме. "
        if not self.program.check_age(age=self.person.age):
            text += "Заемщик не подходит по возрасту. "
        if not self.person.not_ip():
            text += "ИИН является ИП. "
        if not self.person.not_banned():
            text += "Заемщик в черном списке. "
        return text
        

class Person(models.Model):
    iin = models.CharField(max_length=12,null=False)
    birthday = models.DateField(null=False, blank=True)

    def save(self, *args, **kwargs):
        self.birthday = self.get_birthday_from_iin(self.iin)
        super(Person, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.iin}"
    
    @staticmethod
    def get_birthday_from_iin(iin):
        try:
            dt = datetime.strptime(iin[0:6], '%y%m%d').date()
            return dt
        except:
            raise Exception("Invalid iin") from None
    
    @staticmethod
    def check_ip(iin):
        try:
            url = "https://stat.gov.kz/api/juridical/gov/"
            params = {"bin": iin, "lang": "run"}
            r = requests.get(url, params=params)
            if 'json' in r.headers.get('Content-Type'):
                res = r.json()
                if res['obj'] and res['obj']['ip']:
                    return False
                else:
                    return True
            # return True # returning anyway
        except Exception as e:
            raise Exception(f"Error: {e}") from e
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
    
    def not_ip(self):
        if self.check_ip(self.iin):
            return True
        else:
            return False
         
    def not_banned(self):
        try:
            banned = BanList.objects.get(iin=self.iin)
            if banned:
                return False
        except BanList.DoesNotExist:
            return True 
    

class Program(models.Model):
    min_value = models.PositiveIntegerField(null=False)
    max_value = models.PositiveIntegerField(null=False)
    min_age = models.PositiveSmallIntegerField(null=False)
    max_age = models.PositiveSmallIntegerField(null=False)

    def __str__(self):
        return f"{self.id}"
    
    def check_sum(self, sum):
        try:
            if self.min_value < sum < self.max_value:
                return True
            else:
                return False
        except:
            raise Exception("Invalid sum or program") from None
    
    def check_age(self, age):
        try:
            if self.min_age < age < self.max_age:
                return True
            else:
                return False
        except:
            raise Exception("Invalid age or program") from None
                

class CreditRequest(models.Model):
    program = models.ForeignKey(Program, 
                on_delete=models.PROTECT, 
                related_name='programs')
    person = models.ForeignKey(Person, 
                on_delete=models.PROTECT, 
                related_name='persons')
    sum = models.PositiveIntegerField(null=False)
    STATUS = (
        (0, "OK"),
        (1, "Decline"),
    )
    status = models.IntegerField(choices=STATUS)
    decline = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        validate = ValidateRequest(program=self.program, person=self.person, sum=self.sum)
        print(f"Validate: {validate}")
        if validate.status:
            self.status = 0
        else:
            self.status = 1
            self.decline = validate.text
        super(CreditRequest, self).save(*args, **kwargs)


class BanList(models.Model):
    iin = models.CharField(max_length=12,null=False)

    def __str__(self):
        return f"Banned: {self.iin}"