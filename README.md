## Red Hat OpenStack Platform Survey
Mark Lamourine  
<markllama@gmail.com>

This software is meant to provide visibility and reporting on the
current state of an existing Red Hat OpenStack Platform deployment.

The tool consists of three components.

1. Data Collection - Survey
1. Data Storage - Time Series data
1. Reporting - Text or formatted state and change analysis output

Where possible the components use or integrate with existing
infrastructure: communications, database and presentation.

### Usage

The ospsurvey command is meant to be run on a Director node as the stack user.
It uses the OS_* environment variables for authentication and access to the
undercloud.

The survey results can be reported either as a pretty table or as JSON

### Probes

* RHEL OS Release
* RH OSP Release
* Overcloud Deployment info:
  * Overcloud stack name
  * Overcloud deploy date/time
  * Overcloud update date/time

'''
Revision Number: 0.1.1
Revision Date: Tue Dec 10 21:04:26 UTC 2019
