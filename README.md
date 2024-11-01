<h1>How to use:</h1>

<h3>Calculate CIDR</h3>

1) Execute the script and you will be prompt to enter a CIDR to calculate

<code>python cidr_calculator.py -ip 10.200.10.25/24</code>

![image](https://github.com/user-attachments/assets/2d3b9961-73f9-4319-8881-752127d1800e)

(Optional) You can add the -vertical parameter to display the table in vertical format:

<code>python cidr_calculator.py -ip 10.200.10.25/24 -vertical</code>

![image](https://github.com/user-attachments/assets/d715f2b9-acc0-4de0-95ef-0fb5faac40f0)


<h3>Divide CIDR into multiple Subnets</h3>

2) If you want to divide a given CIDR into multiple subnets just add the -divide argument:

<code>python cidr_calculator.py -ip 10.200.10.25/24 -divide 4</code>

![image](https://github.com/user-attachments/assets/b0017dff-1f44-4ac7-92d8-eca2e28bc9cf)

<h3>Display in Binary Format</h3>

3) If you want to display a given CIDR or Subnet in binary just add the -binary argument:

<code>python cidr_calculator.py -ip 10.200.10.25/24 -binary</code>

![image](https://github.com/user-attachments/assets/fa5ba9aa-340e-4dbf-8107-f97fcf802316)

<code>python cidr_calculator.py -ip 10.200.10.25/24 -binary -vertical</code>

![image](https://github.com/user-attachments/assets/15e3293b-0827-4c30-a800-643e3c41ec11)

<code>python cidr_calculator.py -ip 10.200.10.25/24 -divide 4 -binary</code>

![image](https://github.com/user-attachments/assets/3d2c0c1a-6eca-43a6-89c9-f37e5cec98f7)
