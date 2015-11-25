# Api REST Thug
Thug mimicks the behaviour of Web browsers in order to detect and emulate malicious contents. It make use of Google V8 JavaScript Engine wrapped through PyV8 in order to analyse malicious JavaScript code, and LibEmu library wrapped through PyLibEmu in order to detect and emulate shellcodes.

# Install
Execute in yout console

    docker-compose up

# Use

    #Send Analisys Request
    
    curl -X POST -H "content-type: application/json" \ 
    --data '{"url": "malisiuswebpage.com"}' \ 127.0.0.1:8003/analise
    
    #Response
    {"message": "Analysis In Progress"}
    
    #Recive Report
    curl -X POST -H "content-type: application/json" \ 
    --data '{"url": "malisiuswebpage.com"}' \ 127.0.0.1:8003/report
    
    #Response
    {
	    "status": true,
	    "data": {
		    "behaviors": [
			    {
				    "method": "Dynamic Analysis",
				    ...

**Multiples request in paralel supported**

## Image Size
~616.3 MB