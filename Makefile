start:
	powershell -Command "Start-Job { cd backend; .\.venv\Scripts\activate.ps1; make start }"
	powershell -Command "Start-Job { cd frontend; make start }"
	powershell -Command "Wait-Job *"