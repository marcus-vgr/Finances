if [ ! -d "FinancesEnv" ]; then
	echo "Setting up python environment"
	python -m venv FinancesEnv
	pip install -r requirements.txt
	chmod u+x run.sh 
else
	echo "Python environment already exists! Exitting."
fi
