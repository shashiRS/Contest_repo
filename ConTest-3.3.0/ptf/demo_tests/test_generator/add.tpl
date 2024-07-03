
def SWT_${test_name}v1__each():
     DETAILS("${test_name} verification")

     VERIFIES("${requirement}")

     TESTTAG("hil")

     TESTCASE()

     TESTSTEP("Test for adding numbers ${num_1} and ${num_2}")
     EXPECTED("Result shall be ${result}")
     contest_asserts.verify(${num_1} + ${num_2}, ${result}, "${num_1} + ${num_2} != ${result}")

