Hello!

To use rpc_notebook you need to open 3 powershell (2 is also enough) but I will recommend to use 3

First all 3 files in same folder and open 3 (2) powershell windows when you are in main folder rpc_notebook

#Step1
first start server(s) with "python notebook_server.py 8000" and "python notebook_server.py 8001"

#Step2
Start client in third (or second) Powershell "python notebook_client.py"

#Additional tips
Check: If this is not working check that "notes.xml" is in same folder
Check: "netstat -ano | findstr :8000" and "netstat -ano | findstr :8001"
