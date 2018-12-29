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

# use system logging
import logging

import xml.etree.ElementTree as Xml
import re


# XXXXXX still here for backwards compatibility
# these are common tags for both cascade-choice and dynamic-reference
SCRIPT_OPTIONAL = [
    # fields( yaml tag, xml tag, default value )
    ('script-sandbox', 'sandbox', 'False'),
    ('script-classpath', 'classpath', 'False'),
]

# XXXXXX still here for backwards compatibility
FALLBACK_OPTIONAL = [
    # fields( yaml tag, xml tag, default value )
    ('fallback-sandbox', 'sandbox', 'False'),
    ('fallback-classpath', 'classpath', 'False'),
]


def _to_str(x):
    if not isinstance(x, (str, unicode)):
        return str(x).lower()
    return x


def _add_element(xml_parent, tag, value):
    Xml.SubElement(xml_parent, tag).text = _to_str(value)


# XXXXXX still here for backwards compatibility
def _add_script(xml_parent, tag, value):
    section = Xml.SubElement(xml_parent, tag)
    Xml.SubElement(section, "script").text = value
    Xml.SubElement(section, "sandbox").text = "false"


def _add_sandbox(xml_parent, data):
    if data:
        # check for true/false
        if not re.match(r"(true|false)", _to_str(data)):
            raise Exception("sandbox must be true or false, not this: '%s'" % _to_str(data))
        else:
            _add_element(xml_parent, 'sandbox', _to_str(data))
    else:
        # default
        _add_element(xml_parent, 'sandbox', 'false')


def _add_classpath(xml_parent, data):
    if data:
        # create the classpath section
        section = Xml.SubElement(xml_parent, 'classpath')
        # add the elements
        uri_match = re.compile(r"(file:/|https*://)", re.IGNORECASE)
        for url in [x.strip() for x in data.split(',')]:
            if uri_match.match(url):
                _add_element(section, 'entry', url)
            else:
                raise Exception("classpath entries must start with file:/... or http[s]://... : %s" % url)


def _add_groovy(xml_parent, param_name, groovy_data, fallback_data):
    script_section = Xml.SubElement(xml_parent, 'script', {'class': 'org.biouno.unochoice.model.GroovyScript'})

    script = groovy_data.get('script')
    if script:
        section = Xml.SubElement(script_section, 'secureScript')
        _add_element(section, 'script', script)
        _add_sandbox(section, groovy_data.get('sandbox'))
        _add_classpath(section, groovy_data.get('classpath'))
    else:
        raise Exception("missing groovy script argument in %s" % param_name)

    if fallback_data:
        script = fallback_data.get('script')
        if script:
            section = Xml.SubElement(script_section, 'secureFallbackScript')
            _add_element(section, 'script', script)
            _add_sandbox(section, fallback_data.get('sandbox'))
            _add_classpath(section, fallback_data.get('classpath'))


def _add_scriptler_parameters(xml_parent, data):
    # create the parameters section
    parameters = Xml.SubElement(xml_parent, 'parameters', {'class': 'linked-hash-map'})
    if data:
        # add the parameters
        for d in data:
            for k, v in d.items():
                entry = Xml.SubElement(parameters, 'entry')
                _add_element(entry, "string", k)
                _add_element(entry, "string", v)


def _add_scriptler(xml_parent, param_name, data):
    section = Xml.SubElement(xml_parent, 'script', {'class': 'org.biouno.unochoice.model.ScriptlerScript'})

    script = data['script']
    if script:
        _add_element(section, "scriptlerScriptId", script)
        _add_scriptler_parameters(section, data.get('parameters'))
    else:
        raise Exception("missing Scriptler script argument in %s" % param_name)


def _unique_string(project, name):
    return 'choice-param-{0}-{1}'.format(project, name).lower()


# XXXXXXX still here for backwards compatibility
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
        # fields(yaml tag)
        ('name', 'name'),
        ('project', 'projectName'),
    ]

    OPTIONAL = [
        # fields( yaml tag, xml tag, default value )
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
    # add calculated fields
    logging.debug('cascade_choice data: %s' % data['project'])
    _add_element(section, 'randomName', _unique_string(data['project'], data['name']))


# XXXXXXX still here for backwards compatibility
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
        If your script creates an input HTML element, you can check this option and the value input field will
        be omitted.
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
        # fields(yaml tag)
        ('name', 'name'),
        ('project', 'projectName')
    ]

    OPTIONAL = [
        # fields( yaml tag, xml tag, default value )
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
    # add calculated fields
    _add_element(section, 'randomName', _unique_string(data['project'], data['name']))


def _common_steps(xml_parent, element_name, REQUIRED, OPTIONAL, CHOICE_TYPE, data):
    logging.debug('_common_steps data: data = %s' % data)

    section = Xml.SubElement(xml_parent, element_name)

    for name, tag in REQUIRED:
        try:
            _add_element(section, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    param_name = data.get('name')
    logging.debug('_common_steps data: param_name = %s' % param_name)
    project = data.get('project')
    logging.debug('_common_steps data: project = %s' % project)

    for name, tag, default in OPTIONAL:
        _add_element(section, tag, data.get(name, default))

    # check to see which scripts were defined
    groovy = data.get('groovy')
    fallback = data.get('fallback')
    scriptler = data.get('scriptler')

    # if neither groovy nor scriptler, raise an error
    if not groovy and not scriptler:
        raise Exception("missing script argument. need either groovy or scriptler in parameter %s" % param_name)

    # if both groovy/fallback and scriptler, raise an error
    if (groovy or fallback) and scriptler:
        raise Exception("illegal use of both groovy/fallback and scriptler scripts in the same parameter %s"
                        % param_name)

    # at this point, we know it's either groovy/fallback or scriptler, but not both
    if groovy:
        # add groovy, along with optional fallback
        _add_groovy(section, param_name, groovy, fallback)
    elif scriptler:
        # add scriptler
        _add_scriptler(section, param_name, scriptler)

    # set the choice-type
    _add_element(section, 'choiceType', CHOICE_TYPE[data.get('choice-type', 'default')])

    # add an empty parameters section
    # not sure why this is needed, but this is what the active choice plug-in does, so...
    Xml.SubElement(section, 'parameters', {'class': 'linked-hash-map'})

    # add calculated fields
    _add_element(section, 'randomName', _unique_string(project, param_name))


def active_choice(parser, xml_parent, data):
    """yaml: active-choice
    Creates an active choice parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter (REQUIRED)
    :arg str project: the project name (not really used for anything so any value will do) (REQUIRED)
    :arg str description: a description of the parameter (OPTIONAL)
    # REQUIRED: YOU MUST USE EITHER groovy or scripter, not both
    :arg hash-map groovy: the section to define the main groovy script to generate the values for this parameter
        :arg str script: the actual groovy script
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map fallback: the section to define the fallback groovy script to generate the values when the main
        groovy fails (OPTIONAL)
        :arg str script: the actual fallback groovy script (REQIRED, IF you define fallback)
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map scriptler: the section to define the main groovy script to generate the values for this parameter
        :arg str script: simple file name of the scriptler script from the system library of scripts; not an
            absolute path (REQIRED, IF you define scriptler)
        :arg list parameters: list of parameters (OPTIONAL; key-value pairs)
            :arg key-value "<KEYNAME>: <VALUE>"
            ...
    arg: str choice-type: a choice type, can be on of single, multi, radio, checkbox (OPTIONAL; default single)
    arg: bool filterable: provide interactive filtering (OPTIONAL; default false)
    arg: bool filter-length: number of lines to show in the filter (OPTIONAL; default 1)
    Example::

    .. code-block:: yaml

    # using groovy
    - active-choice:
          name: ACTIVE_CHOICE_01
          project: 'active-choice-example'
          description: "A parameter named ACTIVE_CHOICE_01 with options foo and bar."
          groovy:
              script: |
                  return ['foo:selected', 'bar']
              classpath: /your-path/some-java.jar
              sandbox: true
          fallback:
              script: |
                  return ['Error']
          visible-item-count: 1
          choice-type: single

    # using scriptler
    - active-choice:
          name: ACTIVE_CHOICE_01
          project: 'active-choice-example'
          description: "A parameter named ACTIVE_CHOICE_01 with options foo and bar."
          scriptler:
              script: foo-bar-scriptler
              parameters:
                  - PARAM1:  some-value01
                  - PARAM2:  some-value02
          visible-item-count: 1
          choice-type: single

    """

    CHOICE_TYPE = {
        'default': 'PT_SINGLE_SELECT',
        'single': 'PT_SINGLE_SELECT',
        'multi': 'PT_MULTI_SELECT',
        'checkbox': 'PT_CHECKBOX',
        'radio': 'PT_RADIO',
    }

    REQUIRED = [
        # fields(yaml tag)
        ('name', 'name'),
        ('project', 'projectName'),
    ]

    OPTIONAL = [
        # fields( yaml tag, xml tag, default value )
        ('description', 'description', ''),
        ('visible-item-count', 'visibleItemCount', 1),
        ('filterable', 'filterable', False),
        ('filter-length', 'filterLength', 1)
    ]

    element_name = 'org.biouno.unochoice.ChoiceParameter'
    logging.debug('active_choice data: data = %s' % data)
    _common_steps(xml_parent, element_name, REQUIRED, OPTIONAL, CHOICE_TYPE, data)


def active_choice_reactive(parser, xml_parent, data):
    """yaml: active-choice-reactive
    Creates an active choice reactive parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter (REQUIRED)
    :arg str project: the project name (not really used for anything so any value will do) (REQUIRED)
    :arg str description: a description of the parameter (OPTIONAL)
    # REQUIRED: YOU MUST USE EITHER groovy or scripter, not both
    :arg hash-map groovy: the section to define the main groovy script to generate the values for this parameter
        :arg str script: the actual groovy script
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map fallback: the section to define the fallback groovy script to generate the values when the main
        groovy fails (OPTIONAL)
        :arg str script: the actual fallback groovy script (REQIRED, IF you define fallback)
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map scriptler: the section to define the main groovy script to generate the values for this parameter
        :arg str script: simple file name of the scriptler script from the system library of scripts; not an
            absolute path (REQIRED, IF you define scriptler)
        :arg list parameters: list of parameters (OPTIONAL; key-value pairs)
            :arg key-value "<KEYNAME>: <VALUE>"
            ...
    arg: str choice-type: a choice type, can be on of single, multi, radio, checkbox (OPTIONAL; default single)
    arg: bool filterable: provide interactive filtering (OPTIONAL; default false)
    arg: bool filter-length: number of lines to show in the filter (OPTIONAL; default 1)
    arg: str reference: comma-separated list of other PARAMETERS to which this one will react (OPTIONAL; but if you
        leave it out, what's the point?)
    Example::

    .. code-block:: yaml

    # using groovy
    - active-choice-reactive:
          name: ACTIVE_CHOICE_REACTIVE_01
          project: 'active-choice-reactive-example'
          description: "A parameter named ACTIVE_CHOICE_REACTIVE_01 with options foo and bar."
          groovy:
              script: |
                  return ['foo:selected', 'bar']
              classpath: /your-path/some-java.jar
              sandbox: true
          fallback:
              script: |
                  return ['Error']
          visible-item-count: 1
          reference: STR_PARAM,CHOICE_PARAM
          choice-type: single

    # using scriptler
    - active-choice-reactive:
          name: ACTIVE_CHOICE_REACTIVE_02
          project: 'active-choice-reactive-example'
          description: "A parameter named ACTIVE_CHOICE_REACTIVE_02 with options foo and bar."
          scriptler:
              script: foo-bar-scriptler
              parameters:
                  - PARAM1:  some-value01
                  - PARAM2:  some-value02
          visible-item-count: 1
          reference: STR_PARAM,CHOICE_PARAM
          choice-type: single

    """

    CHOICE_TYPE = {
        'default': 'PT_SINGLE_SELECT',
        'single': 'PT_SINGLE_SELECT',
        'multi': 'PT_MULTI_SELECT',
        'checkbox': 'PT_CHECKBOX',
        'radio': 'PT_RADIO',
    }

    REQUIRED = [
        # fields(yaml tag)
        ('name', 'name'),
        ('project', 'projectName'),
    ]

    OPTIONAL = [
        # fields( yaml tag, xml tag, default value )
        ('description', 'description', ''),
        ('visible-item-count', 'visibleItemCount', 1),
        ('reference', 'referencedParameters', ''),
        ('filterable', 'filterable', False),
        ('filter-length', 'filterLength', 1)
    ]

    element_name = 'org.biouno.unochoice.CascadeChoiceParameter'
    logging.debug('active_choice_reactive data: data = %s' % data)
    _common_steps(xml_parent, element_name, REQUIRED, OPTIONAL, CHOICE_TYPE, data)


def active_choice_reactive_reference(parser, xml_parent, data):
    """yaml: active-choice-reactive-reference
    Creates an active choice reactive reference parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter (REQUIRED)
    :arg str project: the project name (not really used for anything so any value will do) (REQUIRED)
    :arg str description: a description of the parameter (OPTIONAL)
    # REQUIRED: YOU MUST USE EITHER groovy or scripter, not both
    :arg hash-map groovy: the section to define the main groovy script to generate the values for this parameter
        :arg str script: the actual groovy script
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map fallback: the section to define the fallback groovy script to generate the values when the main
        groovy fails (OPTIONAL)
        :arg str script: the actual fallback groovy script (REQIRED, IF you define fallback)
        :arg str classpath: additional class paths for your groovy code (OPTIONAL; URLs of the form file:/...
            or http[s]://...)
        :arg str sandbox: run this script in a sandbox (OPTIONAL; default false)
    :arg hash-map scriptler: the section to define the main groovy script to generate the values for this parameter
        :arg str script: simple file name of the scriptler script from the system library of scripts; not an
            absolute path (REQIRED, IF you define scriptler)
        :arg list parameters: list of parameters (OPTIONAL; key-value pairs)
            :arg key-value "<KEYNAME>: <VALUE>"
            ...
    arg: str choice-type: a choice type, can be on of single, multi, radio, checkbox (OPTIONAL; default single)
    arg: bool filterable: provide interactive filtering (OPTIONAL; default false)
    arg: bool filter-length: number of lines to show in the filter (OPTIONAL; default 1)
    arg: str reference: comma-separated list of other PARAMETERS to which this one will react (OPTIONAL; but if you
        leave it out, what's the point?)
    Example::

    .. code-block:: yaml

    # using groovy
    - active-choice-reactive-reference:
          name: ACTIVE_CHOICE_REACTIVE_REFERENCE_01
          project: 'active-choice-reactive-reference-example'
          description: "A parameter named ACTIVE_CHOICE_REACTIVE_REFERENCE_01 with options foo and bar."
          groovy:
              script: |
                  return ['foo:selected', 'bar']
              classpath: /your-path/some-java.jar
              sandbox: true
          fallback:
              script: |
                  return ['Error']
          visible-item-count: 1
          reference: STR_PARAM,CHOICE_PARAM
          choice-type: input-text

    # using scriptler
    - active-choice-reactive-reference:
          name: ACTIVE_CHOICE_REACTIVE_REFERENCE_02
          project: 'active-choice-reactive-reference-example'
          description: "A parameter named ACTIVE_CHOICE_REACTIVE_REFERENCE_02 with options foo and bar."
          scriptler:
              script: foo-bar-scriptler
              parameters:
                  - PARAM1:  some-value01
                  - PARAM2:  some-value02
          visible-item-count: 1
          reference: STR_PARAM,CHOICE_PARAM
          choice-type: input-text

    """

    CHOICE_TYPE = {
        'default': 'ET_TEXT_BOX',
        'input-text': 'ET_TEXT_BOX',
        'numbered-list': 'ET_ORDERED_LIST',
        'bullet-list': 'ET_UNORDERED_LIST',
        'formatted-html': 'ET_FORMATTED_HTML',
        'formatted-hidden-html': 'ET_FORMATTED_HIDDEN_HTML'
    }

    REQUIRED = [
        # fields(yaml tag)
        ('name', 'name'),
        ('project', 'projectName'),
    ]

    OPTIONAL = [
        # fields( yaml tag, xml tag, default value )
        ('description', 'description', ''),
        ('visible-item-count', 'visibleItemCount', 1),
        ('reference', 'referencedParameters', ''),
        ('filterable', 'filterable', False),
        ('filter-length', 'filterLength', 1)
    ]

    element_name = 'org.biouno.unochoice.DynamicReferenceParameter'
    logging.debug('active_choice_reactive_reference data: data = %s' % data)
    _common_steps(xml_parent, element_name, REQUIRED, OPTIONAL, CHOICE_TYPE, data)
