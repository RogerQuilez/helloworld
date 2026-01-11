pipeline {
    agent any

    environment {
        VENV = "venv"
        JMETER_HOME = "C:\\apache-jmeter-5.6.3"
    }

    stages {

        stage('Setup') {
            steps {
                bat """
                    REM Crear virtualenv y actualizar pip
                    python -m venv %VENV%
                    %VENV%\\Scripts\\python.exe -m pip install --upgrade pip
                    REM Instalar todas las dependencias necesarias
                    %VENV%\\Scripts\\python.exe -m pip install pytest requests flake8 bandit coverage
                """
            }
        }

        stage('Unit Tests') {
            steps {
                bat """
                    REM Ejecutar tests unitarios
                    %VENV%\\Scripts\\python.exe -m pytest test\\unit --junitxml="%CD%\\unit-results.xml"
                """
            }
            post {
                always {
                    junit 'unit-results.xml'
                }
            }
        }

        stage('Start App') {
            steps {
                bat """
                    REM Levantar la app Flask en background
                    start /B %VENV%\\Scripts\\python.exe app\\api.py
                    REM Esperar unos segundos para que el servidor arranque
                    timeout /t 5 /nobreak
                """
            }
        }

        stage('REST Tests') {
            steps {
                bat """
                    REM Ejecutar tests REST
                    %VENV%\\Scripts\\python.exe -m pytest test\\rest --junitxml="%CD%\\rest-results.xml"
                """
            }
            post {
                always {
                    junit 'rest-results.xml'
                }
            }
        }

        stage('Stop App') {
            steps {
                bat """
                    REM Detener la app Flask levantada en background
                    taskkill /IM python.exe /F
                """
            }
        }

        stage('Static Analysis') {
            steps {
                bat """
                    REM Analizar código con flake8
                    %VENV%\\Scripts\\python.exe -m flake8 app
                """
            }
        }

        stage('Security Test') {
            steps {
                bat """
                    REM Analizar seguridad con bandit
                    %VENV%\\Scripts\\bandit -r app
                """
            }
        }

        stage('Performance') {
            steps {
                bat """
                    REM Ejecutar tests de rendimiento con JMeter
                    mkdir jmeter-results
                    "%JMETER_HOME%\\bin\\jmeter.bat" -n -t test\\jmeter\\flask.jmx -l jmeter-results\\results.jtl -e -o jmeter-results\\report
                """
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'jmeter-results\\report',
                        reportFiles: 'index.html',
                        reportName: 'JMeter Performance Report'
                    ])
                }
            }
        }

        stage('Coverage') {
            steps {
                bat """
                    REM Generar reporte de coverage
                    %VENV%\\Scripts\\python.exe -m coverage run -m pytest
                    %VENV%\\Scripts\\python.exe -m coverage html
                """
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }

    post {
        always {
            bat """
                REM Limpiar virtualenv
                rmdir /s /q %VENV%
            """
        }
    }
}