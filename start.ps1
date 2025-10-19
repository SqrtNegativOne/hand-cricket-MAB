# start-servers.ps1

# Start backend in a new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd "C:\Users\arkma\Documents\GitHub\hand-cricket-MAB\backend"; .\.venv\Scripts\activate.ps1; make start'

# Start frontend in a new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd "C:\Users\arkma\Documents\GitHub\hand-cricket-MAB\frontend"; make start'
