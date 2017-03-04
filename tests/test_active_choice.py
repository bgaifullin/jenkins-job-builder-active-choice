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

import glob
import os
from xml.dom import minidom

from jenkins_jobs import parser

import pytest


class Scenario(object):
    def __init__(self, name, test_input, expected):
        self.name = name
        self.test_input = test_input
        self.expected = expected


def get_scenarios():
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
    for path in glob.iglob(os.path.join(fixtures_path, "*.yaml")):
            wo_ext = os.path.splitext(path)[0]
            yield Scenario(os.path.basename(wo_ext), path, wo_ext + ".xml")


def generate_xml(fn):
    yaml_parser = parser.YamlParser()
    yaml_parser.parse(fn)
    yaml_parser.expandYaml()
    assert 1 == len(yaml_parser.jobs), "Expected one job"
    return yaml_parser.getXMLForJob(yaml_parser.jobs[0]).output()


def load_xml(fn):
    with open(fn, "rb") as stream:
        return stream.read().encode("utf-8")


@pytest.mark.parametrize("scenario", get_scenarios(), ids=lambda x: x.name)
def test_scenario(scenario):
    actual = generate_xml(scenario.test_input)
    expected = load_xml(scenario.expected)
    print(actual)
    print(expected)
    assert actual == expected, "check result xml"
