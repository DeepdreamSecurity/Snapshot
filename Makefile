install:
	pip install -r requirements.txt

run-lite:
	python main.py --client example.com --tier lite

run-deep:
	python main.py --client example.com --tier deep

pdf:
	python scripts/render_pdf.py reports/example.com_lite.html reports/example.com_lite.pdf
