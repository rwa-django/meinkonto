from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils import timezone
from django.conf import settings

# Account Type
class Account_Type(models.Model):
    login = models.CharField(max_length=200)
    type = models.CharField(max_length=10,
                            default='B',
                            help_text="Type")
    pos = models.SmallIntegerField(default=1)
    aktiv = models.BooleanField(default=False,
                                help_text="Aktiv")
    label = models.CharField(max_length=200,
                             help_text="Beschreibung")

    def __str__(self):
        return '{0}({1}-{2}) {3}'.format(self.login, self.type, self.label, self.aktiv)

    class Meta:
        unique_together = (('login', 'pos'),)
        ordering = ['login', 'pos']           # sortierung mit - dreht die Sortierung


# Account Base Data
class Account_Base(models.Model):
    login = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              editable=True)
    account_type = models.ForeignKey(Account_Type,
                                     default=1,
                                     on_delete=models.CASCADE)
    account_amount = models.DecimalField(default=0,
                                         max_digits=10,
                                         decimal_places=2)
    account_info = models.CharField(max_length=200,
                                    help_text="Buchungs Info")
    account_start_day = models.PositiveSmallIntegerField(default=0,
                                                         validators=[
                                                             MinValueValidator(0),
                                                             MaxValueValidator(30)],
                                                         help_text="Format: <MM>")

    def __str__(self):
        return '{0} {1} {2}.- {3}'.format(self.login, self.account_type, self.account_amount, self.account_info)


# Account
class Account(models.Model):
    login = models.CharField(max_length=200,
                             help_text="Login")
    account_type = models.ForeignKey(Account_Type,
                                  on_delete=models.CASCADE)
    account_year = models.PositiveSmallIntegerField(default=datetime.now().year,
                                                    validators=[
                                                        MinValueValidator(2018),
                                                        MaxValueValidator(2050)],
                                                    help_text="Format: <YYYY>")
    account_month = models.PositiveSmallIntegerField(default=0,
                                                     validators=[
                                                        MinValueValidator(0),
                                                        MaxValueValidator(12)],
                                                     help_text="Format: <MM>")
    account_amount = models.DecimalField(max_digits=10,
                                         decimal_places=2)
    current_amount = models.DecimalField(max_digits=10,
                                         decimal_places=2)
    account_info = models.CharField(max_length=200,
                                    help_text="Buchungs Info")
    account_booked = models.DateTimeField(default=timezone.now,
                                          editable=False)

    def __str__(self):
        return '{0} {1} - {2}/{3} - {4}'.format(self.login, self.account_type, self.account_amount, self.account_year, self.account_month)


# Account Position
class Account_Pos(models.Model):
    account_id = models.ForeignKey(Account,
                                  on_delete=models.CASCADE)
    pos = models.SmallIntegerField(default=1)
    booking_date = models.DateTimeField(default=datetime.now())
    booking_amount = models.DecimalField(default=0,
                                         max_digits=10,
                                         decimal_places=2)
    booking_info = models.CharField(max_length=200,
                                    help_text="Buchungs Info")
    booking_booked = models.DateTimeField(default=timezone.now,
                                          editable=False)

    class Meta:
        unique_together = (('account_id', 'pos'),)
        ordering = ["account_id", "-pos"]           # sortierung mit - dreht die Sortierung

    def __str__(self):
        return '{0} / - / {1} {2}.- {3}'.format(self.account_id, self.pos, int(self.booking_amount), self.booking_info)

