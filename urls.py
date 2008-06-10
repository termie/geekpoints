# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'geekr.views.index'),
    (r'^(?P<nick>[\w\_\.]+)$', 'geekr.views.score'),
    (r'^(?P<nick>[\w\_\.]+)/verbose', 'geekr.views.verbose'),
    (r'^(?P<nick>[\w\_\.]+)/plusplus', 'geekr.views.inc', {'after': False, 'value': 1}),
    (r'^(?P<nick>[\w\_\.]+)/minusminus', 'geekr.views.inc', {'after': False, 'value': -1}),
    (r'^plusplus/(?P<nick>[\w\_\.]+)', 'geekr.views.inc', {'after': True, 'value': 1}),
    (r'^minusminus/(?P<nick>[\w\_\.]+)', 'geekr.views.inc', {'after': True, 'value': -1}),

    # Example:
    # (r'^foo/', include('foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
