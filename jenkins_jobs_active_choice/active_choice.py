# Copyright 2016 Bulat Gaifullin
#
# This file is part of jenkins-job-builder-active-choice
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import xml.etree.ElementTree as Xml


CHOICE_TYPE = {
    'single': 'PT_SINGLE_SELECT',
    'multi': 'PT_MULTI_SELECT',
    'checkbox': 'PT_CHECKBOX',
    'radio': 'PT_RADIO',
}

REQUIRED = [
    # (yaml tag, xml tag)
    ('name', 'name', ''),
    ('script', 'script', 'script'),
    ('project', 'projectName', ''),
]

OPTIONAL = [
    # ( yaml tag, xml tag, default value )
    ('description', 'description', '', ''),
    ('visible-item-count', 'visibleItemCount', 1, ''),
    ('fallback-script', 'fallbackScript', '', 'script'),
    ('reference', 'referencedParameters', '', ''),
    ('choice-type', 'choiceType', 'single', ''),
    ('filterable', 'filterable', False, ''),
]


def _to_str(x):
    if not isinstance(x, str):
        return str(x).lower()
    return x


def _add_element(xml_parent, tag, value):
    Xml.SubElement(xml_parent, tag).text = _to_str(value)


def _unique_string(project, name):
    return 'param-name-{0}-{1}'.format(project, name).lower()


def active_choice_parameter(parser, xml_parent, data):
    """yaml: active-choice
    Creates an active choice parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter
    :arg str script: the groovy script which generates choices
    :arg str description: a description of the parameter (optional)
    arg: int visible-item-count: a number of visible items
    arg: str fallback-script: a groovy script which will be evaluated if main script fails (optional)
    arg: str reference: the name of parameter on changing that the parameter will be re-evaluated
    arg: str choice-type: a choice type, can be on of single, multi, checkbox or radio
    arg: bool filterable: added text box to filter elements
    Example::

    .. code-block:: yaml

        - active-choice:
          name: ACTIVE_CHOICE
          project: test_project
          script: |
            return ['foo', 'bar']
    """

    element_name = 'org.biouno.unochoice.CascadeChoiceParameter'

    pdef = Xml.SubElement(xml_parent, element_name)
    script_section = Xml.SubElement(pdef, 'script', {'class': 'org.biouno.unochoice.model.GroovyScript'})
    Xml.SubElement(xml_parent, 'parameters', {'class': 'linked-hash-map'})
    sections = {'': pdef, 'script': script_section}

    for name, tag, section in REQUIRED:
        try:
            _add_element(sections[section], tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    for name, tag, default, section in OPTIONAL:
        _add_element(sections[section], tag, data.get(name, default))

    # added calculated fields
    _add_element(pdef, 'randomName', _unique_string(data['project'], data['name']))
