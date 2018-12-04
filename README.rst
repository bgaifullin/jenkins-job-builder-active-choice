Jenkins Job Builder plugin for Active Choice Parameter
======================================================

.. image:: https://travis-ci.org/bgaifullin/jenkins-job-builder-active-choice.png?branch=master
    :target: https://travis-ci.org/bgaifullin/jenkins-job-builder-active-choice
.. image:: https://img.shields.io/pypi/v/jenkins-job-builder-active-choice.svg
    :target: https://pypi.python.org/pypi/jenkins-job-builder-active-choice

Enables support for `Active Choice Plugin`_ plugin in `Jenkins Job Builder`_.

Example:

.. code-block:: yaml

    # OLD: partial support of Active Choice Plug-in capabilities
    # deprecated -- see below
    - job:
        name: 'cascade-choice-example'

        parameters:
          - string:
              name: STR_PARAM
              default: test
          - cascade-choice:
              project: 'cascade-choice-example'
              name: CASCADE_CHOICE
              script: |
                return ['foo:selected', 'bar']
              description: "A parameter named CASCADE_CHOICE which options foo and bar."
              visible-item-count: 1
              fallback-script: |
                return ['Something Wrong']
              reference: STR_PARAM
              choice-type: single
          - dynamic-reference:
              name: DYNAMIC_REF
              project: 'dynamic-reference-example-04'
              script: |
                return ['foo', 'bar']
              description: "A parameter named DYNAMIC_REF with options foo and bar."
              fallback-script: |
                return ['Something Wrong']
              reference: STR_PARAM
              omit-value: false
              choice-type: bullet-list

    # NEW: Supports full capabilities of the Active Choice Plug-in
    - job:
        name: 'TEST-jjb-active-choice-full-support'
  
        parameters:
            - string:
                name: STR_PARAM
                default: test
  
            - choice:
                name: CHOICE_PARAM
                choices:
                  - choice_01
                  - choice_02
                  - choice_03
                  - choice_04
                description: |
                  Just a test parameter for used by references
  
            - active-choice:
                project: 'active-choice-example'
                name: ACTIVE_CHOICE_01
                description: "A parameter named ACTIVE_CHOICE_01 with options foo and bar."
                groovy:
                    script: |
                        return ['foo:selected', 'bar']
                    classpath: file:/tmp/aklsdjfkl.jar
                    sandbox: false        
                fallback:
                    script: |
                        return ['Error']
                visible-item-count: 1
                choice-type: single
                filterable:  true
                filter-length: 3
  
            - active-choice-reactive:
                project: 'active-choice-example'
                name: ACTIVE_CHOICE_REACTIVE_01
                description: "A parameter named ACTIVE_CHOICE_REACTIVE_01 with options foo and bar."
                groovy:
                    script: |
                        return ['foo:selected', 'bar']
                    classpath: file:/tmp/aklsdjfkl.jar
                fallback:
                    script: |
                        return ['Error']
                    classpath: file:/tmp/aklsdjfkl.jar,https://lakjsdfklsdjklf/lkajsdflk.jar
                    sandbox: true    
                visible-item-count: 10
                reference: STR_PARAM,CHOICE_PARAM
                choice-type: multi
  
            - active-choice-reactive-reference:
                name: ACTIVE_CHOICE_REACTIVE_REF_01
                project: 'active-choice-example'
                description: "A parameter named ACTIVE_CHOICE_REACTIVE_REF_01 with options foo and bar."
                groovy:
                    script: |
                        return ['foo:selected', 'bar']
                    classpath: file:/tmp/aklsdjfkl.jar
                    sandbox: true    
                fallback:
                    script: |
                        return ['Error']
                    classpath: file:/tmp/aklsdjfkl.jar,http://lakjsdfklsdjklf/lkajsdflk.jar
                reference: STR_PARAM,CHOICE_PARAM
                omit-value: false
                choice-type: bullet-list


.. _`Active Choice Plugin`: https://wiki.jenkins-ci.org/display/JENKINS/Active+Choices+Plugin
.. _`Jenkins Job Builder`: http://docs.openstack.org/infra/jenkins-job-builder/index.html
.. _`example`: tests/fixtures/case-001.yaml
