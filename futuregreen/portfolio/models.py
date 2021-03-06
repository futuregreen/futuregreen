# projects/models.py

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.db.models import Max
from django.utils.html import strip_tags

from taggit.managers import TaggableManager
from categories.models import Category

from futuregreen.images.models import RelatedImageAutoBase
from futuregreen.images.managers import ImageManager

from futuregreen.portfolio.managers import ProjectManager
from futuregreen.people.models import Client, Collaborator, Employee

class ProjectBase(models.Model):
    """
    
        An abstract base class for a project.
    
    """
    
    # project status choices 
    STATUS_LIVE = 1
    STATUS_HIDDEN = 2
    STATUS_PENDING = 3
    STATUS_DRAFT = 4
    STATUS_CHOICES = (
        (STATUS_LIVE, 'Live'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_HIDDEN, 'Hidden'),
    )
    
    # Core fields
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=250)
    short_description = models.TextField()
    description = models.TextField()
    date_start = models.DateField("start date",
                                  blank=True, null=True,
                                  help_text="Leave blank if project is in promo.")
    date_end = models.DateField("end date",
                                help_text="Enter estimated completion date if project is in progress.")

    external_url = models.URLField(blank=True,help_text="Optional.")
    
    # Metadata.
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=STATUS_LIVE,
                                              help_text="Only portfolio with live status will be publicly displayed.")
    featured = models.BooleanField(default=False)
    slug = models.SlugField(unique=True,
                            help_text="Suggested value automatically generated from title. Must be unique.")

    #autogenerated fields
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    # Fields to store generated HTML.
    description_html = models.TextField(editable=False, blank=True)
    
    class Meta:
        abstract = True
        ordering = ('-date_end','name',)

    @permalink
    def get_absolute_url(self):
        return ('portfolio_project_detail', [str(self.slug)])

    def get_next_project(self):
        return self.get_previous_by_date_end(status=self.STATUS_LIVE)

    def get_previous_project(self):
        return self.get_next_by_date_end(status=self.STATUS_LIVE)

    def __unicode__(self):
        return u'%s' % self.name
    
    def render_markup(self):
        """Turns any markup into HTML"""
        original = self.description_html

        if settings.PROJECT_MARKUP == 'markdown':
            import markdown
            self.description_html = markdown.markdown(self.description)
        elif settings.PROJECT_MARKUP == 'textile':
            import textile
            self.description_html = textile.textile(self.description)
        elif settings.PROJECT_MARKUP == 'wysiwyg':
            self.description_html = self.description
        elif settings.PROJECT_MARKUP == 'html':
            self.description_html = self.description
        else:
            self.description_html = strip_tags(self.description)

        return self.description_html != original

    def save(self, force_insert=False, force_update=False):
        self.render_markup()
        super(ProjectBase, self).save(force_insert, force_update)
        
    
class PhysicalMixin(models.Model):
    """

        Fields and methods for a
        physically constructable design project.

    """
    # project size unit choices
    UNIT_SQUAREFOOT = 1
    UNIT_SQUAREMETER = 2
    UNIT_ACRE = 3
    UNIT_HECTARE = 4
    UNIT_CHOICES = (
        (UNIT_SQUAREFOOT, 'square feet'),
        (UNIT_SQUAREMETER, 'square meters'),
        (UNIT_ACRE, 'acres'),
        (UNIT_HECTARE, 'hectares'),
    )
    
    UNIT_CONVERSIONS = {
        (UNIT_SQUAREFOOT, UNIT_SQUAREMETER): Decimal(.0929),
        (UNIT_SQUAREFOOT, UNIT_ACRE): Decimal(.000023),
        (UNIT_SQUAREFOOT, UNIT_HECTARE): Decimal(.0000093),
        (UNIT_SQUAREMETER, UNIT_SQUAREFOOT): Decimal(10.76),
        (UNIT_SQUAREMETER, UNIT_ACRE): Decimal(.00025),
        (UNIT_SQUAREMETER, UNIT_HECTARE): Decimal(.0001),
        (UNIT_ACRE, UNIT_SQUAREFOOT): Decimal(43560),
        (UNIT_ACRE, UNIT_SQUAREMETER): Decimal(4047),
        (UNIT_ACRE, UNIT_HECTARE): Decimal(.4047),
        (UNIT_HECTARE, UNIT_SQUAREFOOT): Decimal(107639.10),
        (UNIT_HECTARE, UNIT_SQUAREMETER): Decimal(10000.00),
        (UNIT_HECTARE, UNIT_ACRE): Decimal(2.47),
    }


    area = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.PositiveSmallIntegerField(choices=UNIT_CHOICES,
                                     default=UNIT_SQUAREFOOT,
                                     help_text="Unit of measurement.")

    area_normalized = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        abstract = True

    def convert(self, someUnit):
        if someUnit == self.unit:
            return self.area
        elif (self.unit, someUnit) in self.UNIT_CONVERSIONS:
            return self.area * self.UNIT_CONVERSIONS[(self.unit, someUnit)]
        else:
            raise Exception("Can't convert")

    @property
    def square_feet(self):
        return self.convert(self.UNIT_SQUAREFOOT)

    @property
    def square_meters(self):
        return self.convert(self.UNIT_SQUAREMETER)

    @property
    def acres(self):
        return self.convert(self.UNIT_ACRE)

    @property
    def hectares(self):
        return self.convert(self.UNIT_HECTARE)

    @property
    def relative_size(self):
        max = self._default_manager.live().aggregate(Max('area_normalized'))['area_normalized__max']
        rel =  (self.area_normalized/max)*100
        

    def save(self, force_insert=False, force_update=False):
        self.area_normalized = self.convert(self.UNIT_SQUAREFOOT)
        super(PhysicalMixin, self).save(force_insert, force_update)
        

class Project(ProjectBase, PhysicalMixin):
    """
        FutureGreen project.

    """

    objects = ProjectManager()

    #address
    address = models.CharField(max_length=255, blank=True, null=True,
                               help_text="Enter the full address of the project")
    
    # relations
    designers = models.ManyToManyField(Employee, blank=True, null=True, related_name='designers')
    builders = models.ManyToManyField(Employee, blank=True, null=True, related_name='builders')
    clients = models.ManyToManyField(Client, blank=True, null=True)
    collaborators = models.ManyToManyField(Collaborator, blank=True, null=True)

    # taxonomy
    tags = TaggableManager(blank=True)
    project_types = models.ManyToManyField('ProjectType', blank=True, null=True)
    landscape_types = models.ManyToManyField('LandscapeType', blank=True, null=True)

    def get_main_image(self):
        return self.projectimage_set.filter(is_main=True)


class ProjectImage(RelatedImageAutoBase):
    """
        Images for a project.

    """
    objects = ImageManager()

    project = models.ForeignKey(Project)


class ProjectType(Category):
    pass

class LandscapeType(Category):
    pass

