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

field_attrs = {'required': '', 'class': 'form-control'}


class CSWRecordForm(forms.ModelForm):
    class Meta:
        model = CSWRecord
        fields = ('source', 'record_type', 'record_format', 'title', 'category', 'abstract',
                  'alternative', 'creator', 'contact_email', 'contact_phone', 'gold')

        widgets = {
            'title': forms.TextInput(attrs=field_attrs),
            'creator': forms.TextInput(attrs=field_attrs),
            'abstract': forms.Textarea(attrs=field_attrs),
            'alternative': forms.TextInput(attrs=field_attrs),
            'source': forms.TextInput(attrs=field_attrs),
            'contact_email': forms.TextInput(attrs=field_attrs),
            'contact_phone': forms.TextInput(attrs=field_attrs),
            'category': forms.Select(attrs=field_attrs),
            'record_type': forms.HiddenInput(),
            'record_format': forms.HiddenInput()
        }

        labels = {
            'source': _('Service Endpoint Url'),
            'title': _('Title'),
            'modified': _('Date Last Modified'),
            'creator': _('Agency/Office'),
            'record_type': _('Type'),
            'alternative': _('Layer Identifier'),
            'abstract': _('Abstract'),
            'record_format': _('Format'),
            'bbox_upper_corner': _('Bounding Box: Upper Corner'),
            'bbox_lower_corner': _('Bounding Box: Lower Corner'),
            'contact_email': _('Contact Email'),
            'contact_phone': _('Contact Phone'),
            'gold': _('Gold'),
            'category': _('Category')
        }

        help_texts = {
            'source': _('e.g. http://example.com/ArcGIS/rest/services/Specialty/ESRI_StateCityHighway_USA/MapServer'),
            'alternative': 'The layer name or ID assigned to the dataset',
            'bbox_upper_corner': _('Coordinates for upper left corner'),
            'bbox_lower_corner': _('Coordinates for lower right corner'),
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
