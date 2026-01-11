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
                    REM Crear virtualenv solo una vez
                    python -m venv %VENV%
                    %VENV%\\Scripts\\pip.exe install --upgrade pip
                """
            }
        }

        stage('Unit Tests') {
            steps {
                bat """
                    REM Instalar pytest y ejecutar tests unitarios
                    %VENV%\\Scripts\\pip.exe install pytest
                    %VENV%\\Scripts\\python.exe -m pytest test\\unit --junitxml=%CD%\\unit-results.xml
                """
            }
            post {
                always {
                    junit 'unit-results.xml'
                }
            }
        }

        stage('REST Tests') {
            steps {
                bat """
                    REM Instalar pytest y requests
                    %VENV%\\Scripts\\pip.exe install pytest requests
                    %VENV%\\Scripts\\python.exe -m pytest test\\rest --junitxml=%CD%\\rest-results.xml
                """
            }
            post {
                always {
                    junit 'rest-results.xml'
                }
            }
        }

        stage('Static Analysis') {
            steps {
                bat """
                    REM Instalar flake8 y analizar código
                    %VENV%\\Scripts\\pip.exe install flake8
                    %VENV%\\Scripts\\python.exe -m flake8 app
                """
            }
        }

        stage('Security Test') {
            steps {
                bat """
                    REM Instalar bandit y analizar seguridad
                    %VENV%\\Scripts\\pip.exe install bandit
                    %VENV%\\Scripts\\bandit -r app
                """
            }
        }

        stage('Performance') {
            steps {
                bat """
                    mkdir jmeter-results
                    %JMETER_HOME%\\bin\\jmeter.bat -n -t test\\jmeter\\flask.jmx -l jmeter-results\\results.jtl -e -o jmeter-results\\report
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
                    REM Instalar coverage y generar reporte
                    %VENV%\\Scripts\\pip.exe install coverage pytest
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
                rmdir /s /q %VENV%
            """
        }
    }
}