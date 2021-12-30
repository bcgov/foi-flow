# Update Failed Reconciliation GL Codes
This document explains the steps to follow when a reconciliation failure occurs.

## Process
- FOI User makes a payment for the FOI Request using credit card
- Overnight batch job on PayBC identifies GL error (invalid GL) which was passed as URL param on payment redirection
- CAS sends email to FOI team with failed transactions numbers
- FOI Technical support team updates the GL code in database manually
- FOI Technical support team runs the job to update the GL code for the failed transactions

## Steps to run the job
<i>Pre-requisite : Make sure the GL codes are updated with correct value before running this.</i>
1. Login to the openshift console.
2. Open terminal of one of the running instance of request-management-api pods.
    OR rsh into the pod from your local machine.
    ```
   oc login 
   oc project <foi namespace>
   oc rsh <request management api pod-name>
   ```
   
3. Run the python job to update the transaction.
    ```
   python update_failed_gl_codes_cli.py -t <comma separated transaction numbers>
   E.g; python update_failed_gl_codes_cli.py -t FOI000000001,FOI000000002,FOI000000003
   ```
 