# contacts/models.py

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink

from taggit.managers import TaggableManager

from futuregreen.contacts.fields import CountryField
from futuregreen.contacts.managers import ContactManager

class ContactBase(models.Model):
    """
    
    Abstract contact model. Includes fields shared
    between all contact types.
        
    """
    objects = ContactManager()

    TYPE_PERSON = 1
    TYPE_COMMERCIAL = 2
    TYPE_EDUCATIONAL = 3
    TYPE_NONPROFIT = 4
    TYPE_GOVERNMENTAL = 5
    TYPE_CHOICES = (
        (TYPE_PERSON, 'Person'),
        (TYPE_COMMERCIAL, 'Commercial Business'),
        (TYPE_EDUCATIONAL, 'Educational Institution'),
        (TYPE_NONPROFIT, 'Non-Profit Organization'),
        (TYPE_GOVERNMENTAL, 'Governmental Organization'),
    )

    # core fields
    user = models.ForeignKey(User, blank=True, null=True)
    contact_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES,
                                                    default=TYPE_PERSON)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField('state/province', max_length=128, blank=True)
    code = models.CharField(max_length=32, blank=True, help_text="Zip or Postal Code")
    country = CountryField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    mobile = models.CharField(max_length=64, blank=True)
    fax = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True, verify_exists=True)

    # metadata
    slug = models.SlugField(unique=True,
                            help_text="Unique web title automatically generated from name.")

    #autogenerated fields
    first_name = models.CharField(max_length=255, blank=True, editable=False)
    middle_name = models.CharField(max_length=255, blank=True, editable=False)
    last_name = models.CharField(max_length=255, blank=True, editable=False)

    # Fields to store generated HTML.
    description_html = models.TextField(editable=False, blank=True)
        
    class Meta:
        abstract = True
        ordering = ('contact_type', 'name',)

    @permalink
    def get_absolute_url(self):
        return ('contacts_contact_detail', [str(self.slug)])

    def __unicode__(self):
        return u'%s' % self.name

    def render_markup(self):
        """Turns any markup into HTML"""
        original = self.description_html
        if settings.CONTACT_MARKUP == 'markdown':
            import markdown
            self.description_html = markdown.markdown(self.description)
        elif settings.CONTACT_MARKUP == 'textile':
            import textile
            self.description_html = textile.textile(self.description)
        elif settings.CONTACT_MARKUP == 'wysiwyg':
            self.description_html = self.description
        elif settings.CONTACT_MARKUP == 'html':
            self.description_html = self.description
        else:
            self.description_html = strip_tags(self.description)

        return self.description_html != original

    def save(self, force_insert=False, force_update=False):
        self.render_markup()
        if self.contact_type == self.TYPE_PERSON:
            names = self.name.split()
            self.first_name = names[0]
            self.last_name = names[-1]
            if len(names) == 3:
                self.middle_name = names[1]
        super(ContactBase, self).save(force_insert, force_update)

class Contact(ContactBase):
    # taxonomy
    tags = TaggableManager(blank=True)

    
class Client(Contact):
    pass

class Collaborator(Contact):
    pass

class EmployeeType(models.Model):
    name =  models.CharField(max_length=255)
    description = models.TextField(blank=True)

    slug = models.SlugField(unique=True,
                            help_text="Suggested value automatically generated from name. Must be unique.")

    def __unicode__(self):
        return u'%s' % self.name

class Employee(Contact):
    # employee status choices
    STATUS_FULL = 1
    STATUS_CONTRACT = 2
    STATUS_FORMER = 3
    STATUS_CHOICES = (
        (STATUS_FULL, 'Full-time'),
        (STATUS_CONTRACT, 'Contract'),
        (STATUS_FORMER, 'Former'),
    )

    # extended core fields
    employee_type = models.ForeignKey(EmployeeType)
    job_title = models.CharField(max_length=250)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=STATUS_FULL)

    def save(self, force_insert=False, force_update=False):
        self.contact_type = self.TYPE_PERSON
        super(Employee, self).save(force_insert, force_update)

