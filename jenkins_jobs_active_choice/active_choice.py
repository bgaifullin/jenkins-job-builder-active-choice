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
# use logging from JJB
import logging


# these are common tags for both cascade-choice and dynamic-reference
SCRIPT_OPTIONAL = [
    # ( yaml tag, xml tag, default value )
    ('script-sandbox', 'sandbox', 'False'),
    ('script-classpath', 'classpath', 'False'),
]

FALLBACK_OPTIONAL = [
    # ( yaml tag, xml tag, default value )
    ('fallback-sandbox', 'sandbox', 'False'),
    ('fallback-classpath', 'classpath', 'False'),
]


def _to_str(x):
    if not isinstance(x, (str, unicode)):
        return str(x).lower()
    return x


def _add_element(xml_parent, tag, value):
    Xml.SubElement(xml_parent, tag).text = _to_str(value)


def _add_script(xml_parent, tag, value):
    section = Xml.SubElement(xml_parent, tag)
    Xml.SubElement(section, "script").text = value
    Xml.SubElement(section, "sandbox").text = "false"


def _unique_string(project, name):
    return 'choice-param-{0}-{1}'.format(project, name).lower()


def _add_script_option(xml_parent, tag, value):
    section = Xml.SubElement(xml_parent, tag)
    Xml.SubElement(section, "script").text = value
    Xml.SubElement(section, "sandbox").text = "false"


def cascade_choice_parameter(parser, xml_parent, data):
    """yaml: cascade-choice
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

        - cascade-choice:
          name: CASCADE_CHOICE
          project: test_project
          script: |
            return ['foo', 'bar']
    """

    CHOICE_TYPE = {
        'single': 'PT_SINGLE_SELECT',
        'multi': 'PT_MULTI_SELECT',
        'checkbox': 'PT_CHECKBOX',
        'radio': 'PT_RADIO',
    }

    REQUIRED = [
        # (yaml tag)
        ('name', 'name'),
        ('project', 'projectName'),
    ]

    OPTIONAL = [
        # ( yaml tag, xml tag, default value )
        ('description', 'description', ''),
        ('visible-item-count', 'visibleItemCount', 1),
        ('reference', 'referencedParameters', ''),
        ('filterable', 'filterable', False),
    ]

    element_name = 'org.biouno.unochoice.CascadeChoiceParameter'

    section = Xml.SubElement(xml_parent, element_name)
    scripts = Xml.SubElement(section, 'script', {'class': 'org.biouno.unochoice.model.GroovyScript'})
    Xml.SubElement(section, 'parameters', {'class': 'linked-hash-map'})

    for name, tag in REQUIRED:
        try:
            _add_element(section, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    for name, tag, default in OPTIONAL:
        _add_element(section, tag, data.get(name, default))

    try:
        _add_script(scripts, "secureScript", data["script"])
    except KeyError:
        raise Exception("missing mandatory argument script")

    _add_script(scripts, "secureFallbackScript", data.get("fallback-script", ""))

    _add_element(section, 'choiceType', CHOICE_TYPE[data.get('choice-type', 'single')])
    # added calculated fields
    logging.debug('cascade_choice data: %s' % data['project'])
    _add_element(section, 'randomName', _unique_string(data['project'], data['name']))


def dynamic_reference_parameter(parser, xml_parent, data):
    """yaml: dynamic-reference
    Creates an active choice dynamic reference parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter
    :arg str script: the groovy script which generates choices
    arg: str fallback-script: a groovy script which will be evaluated if main script fails (optional)
    :arg str description: a description of the parameter (optional)
    arg: str reference: the name(s) of parameter(s) on changing that the parameter will be re-evaluated
    arg: str choice-type: a choice type, can be on of input-text, numbered-list, bullet-list, formatted-html,
         formatted-hidden-html
    arg: bool omit-value: By default Dynamic Reference Parameters always include a hidden input for the value.
         If your script creates an input HTML element, you can check this option and the value input field
         will be omitted.
    Example::

    .. code-block:: yaml

        - dynamic-reference:
          name: DYNAMIC_REF_PARAM
          project: test_project
          script: |
            return ['foo', 'bar']
    """

    CHOICE_TYPE = {
        'input-text': 'ET_TEXT_BOX',
        'numbered-list': 'ET_ORDERED_LIST',
        'bullet-list': 'ET_UNORDERED_LIST',
        'formatted-html': 'ET_FORMATTED_HTML',
        'formatted-hidden-html': 'ET_FORMATTED_HIDDEN_HTML'
    }

    REQUIRED = [
        # (yaml tag)
        ('name', 'name'),
        ('project', 'projectName')
    ]

    OPTIONAL = [
        # ( yaml tag, xml tag, default value )
        ('description', 'description', ''),
        ('reference', 'referencedParameters', ''),
        ('omit-value', 'omitValueField', False)
    ]

    element_name = 'org.biouno.unochoice.DynamicReferenceParameter'

    section = Xml.SubElement(xml_parent, element_name)
    scripts = Xml.SubElement(section, 'script', {'class': 'org.biouno.unochoice.model.GroovyScript'})
    Xml.SubElement(section, 'parameters', {'class': 'linked-hash-map'})

    for name, tag in REQUIRED:
        try:
            _add_element(section, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    for name, tag, default in OPTIONAL:
        _add_element(section, tag, data.get(name, default))

    try:
        _add_script(scripts, "secureScript", data["script"])
    except KeyError:
        raise Exception("missing mandatory argument script")

    _add_script(scripts, "secureFallbackScript", data.get("fallback-script", ""))

    _add_element(section, 'choiceType', CHOICE_TYPE[data.get('choice-type', 'input-text')])
    # added calculated fields
    _add_element(section, 'randomName', _unique_string(data['project'], data['name']))
