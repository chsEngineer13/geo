# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import CSWRecord, CSWRecordReference

field_attrs = {'required': ''}


class CSWRecordForm(forms.ModelForm):
    class Meta:
        model = CSWRecord
        fields = ('source', 'record_type', 'record_format', 'title', 'short_name',
                  'abstract', 'alternative',
                  'keywords', 'classification', 'releasability', 'license',
                  'creator', 'contact_email', 'contact_phone',
                  'srid', 'bbox_upper_corner', 'bbox_lower_corner',
                  'topic_category', 'provenance',
                  'modified', 'maintenance_frequency',
                  'contact_address_type', 'contact_address', 'contact_city', 'contact_state',
                  'contact_country', 'contact_zip', 'fees')

        widgets = {
            'classification': forms.Select(attrs=field_attrs),
            'releasability': forms.Select(attrs=field_attrs),
            'title': forms.TextInput(attrs=field_attrs),
            'short_name': forms.TextInput(attrs=field_attrs),
            'creator': forms.TextInput(attrs=field_attrs),
            'abstract': forms.Textarea(attrs=field_attrs),
            'alternative': forms.TextInput(attrs=field_attrs),
            'srid': forms.TextInput(attrs=field_attrs),
            'bbox_upper_corner': forms.TextInput(attrs=field_attrs),
            'bbox_lower_corner': forms.TextInput(attrs=field_attrs),
            'source': forms.TextInput(attrs=field_attrs),
            'contact_email': forms.TextInput(attrs=field_attrs),
            'contact_phone': forms.TextInput(attrs=field_attrs),
            'contact_address_type': forms.Select(attrs=field_attrs),
            'contact_address': forms.TextInput(attrs=field_attrs),
            'contact_city': forms.TextInput(attrs=field_attrs),
            'contact_state': forms.TextInput(attrs=field_attrs),
            'contact_country': forms.TextInput(attrs=field_attrs),
            'contact_zip': forms.TextInput(attrs=field_attrs),
            'topic_category': forms.Select(attrs=field_attrs),
            'license': forms.Select(attrs=field_attrs),
            'maintenance_frequency': forms.Select(attrs=field_attrs),
            'keywords': forms.TextInput(attrs=field_attrs),
            'fees': forms.TextInput(attrs=field_attrs),
            'provenance': forms.Select(attrs=field_attrs),
            'modified': forms.DateInput(attrs=field_attrs),
            'record_type': forms.HiddenInput(),
            'record_format': forms.HiddenInput()
        }

        labels = {
            'source': _('Service Endpoint Url'),
            'srid': _('SRID'),
            'title': _('Title'),
            'modified': _('Last Content Update Date'),
            'creator': _('Contact Organization'),
            'record_type': _('Type'),
            'alternative': _('Layer Identifier'),
            'abstract': _('Description'),
            'record_format': _('Format'),
            'bbox_upper_corner': _('Bounding Box: Upper Corner'),
            'bbox_lower_corner': _('Bounding Box: Lower Corner'),
            'contact_email': _('Contact Email'),
            'contact_phone': _('Contact Phone'),
            'contact_city': _('Contact City'),
            'contact_state': _('Contact State'),
            'contact_country': _('Contact Country'),
            'contact_zip': _('Contact Postal Code'),
            'contact_address': _('Contact Address'),
            'contact_address_type': _('Contact Address Type'),
            'short_name': _('Short Name'),
            'gold': _('Gold'),
            'topic_category': _('Category')
        }

        help_texts = {
            'source': _('e.g. http://example.com/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer'),
            'alternative': 'The layer name or ID assigned to the dataset',
            'bbox_upper_corner': _('Coordinates for upper left corner'),
            'creator': _('The organization that created the service'),
            'contact_address': _('The address in which the organization resides that created the service'),
            'contact_city': _('The city in which the organization resides that created the service'),
            'contact_state': _('The state in which the organization resides that created the service'),
            'contact_country': _('The country in which the organization resides that created the service'),
            'contact_zip': _('The postal code in which the organization resides that created the service'),
            'bbox_lower_corner': _('Coordinates for lower right corner'),
            'address': _('The address of the organization that created the service.'),
            'fees': _('Text describing the fees imposed when accessing the service. '),
            'abstract': _('A narrative description which provides additional information about the service.'),
            'contact_address_type': _('The address type used by the organization that created the service. '),
            'keywords': _('A list of keywords or keyword phrases describing the service which aid in catalog searching.')

        }


class CSWRecordReferenceForm(forms.ModelForm):
    class Meta:
        model = CSWRecordReference
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'scheme': forms.Select(attrs={'class': 'form-control'})
        }
        exclude = ()


CSWRecordReferenceFormSet = forms.inlineformset_factory(CSWRecord, CSWRecordReference,
                                                        form=CSWRecordReferenceForm, extra=1)