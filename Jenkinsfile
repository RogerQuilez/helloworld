pipeline {
    agent any

    environment {
        VENV = "venv"
        JMETER_HOME = "/opt/jmeter"
    }

    stages {

        stage('Setup') {
            steps {
                sh '''
                    # Crear virtualenv solo una vez
                    python3 -m venv $VENV
                    $VENV/bin/pip install --upgrade pip
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    # Instalar pytest y ejecutar tests unitarios
                    $VENV/bin/pip install pytest
                    $VENV/bin/pytest test/unit --junitxml=$PWD/unit-results.xml
                '''
            }
            post {
                always {
                    junit 'unit-results.xml'
                }
            }
        }

        stage('REST Tests') {
            steps {
                sh '''
                    # Instalar pytest y requests
                    $VENV/bin/pip install pytest requests
                    $VENV/bin/pytest test/rest --junitxml=$PWD/rest-results.xml
                '''
            }
            post {
                always {
                    junit 'rest-results.xml'
                }
            }
        }

        stage('Static Analysis') {
            steps {
                sh '''
                    # Instalar flake8 y analizar código
                    $VENV/bin/pip install flake8
                    $VENV/bin/flake8 app
                '''
            }
        }

        stage('Security Test') {
            steps {
                sh '''
                    # Instalar bandit y analizar seguridad
                    $VENV/bin/pip install bandit
                    $VENV/bin/bandit -r app
                '''
            }
        }

        stage('Performance') {
            steps {
                sh '''
                    mkdir -p jmeter-results
                    $JMETER_HOME/bin/jmeter \
                        -n \
                        -t test/jmeter/flask.jmx \
                        -l jmeter-results/results.jtl \
                        -e \
                        -o jmeter-results/report
                '''
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'jmeter-results/report',
                        reportFiles: 'index.html',
                        reportName: 'JMeter Performance Report'
                    ])
                }
            }
        }

        stage('Coverage') {
            steps {
                sh '''
                    $VENV/bin/pip install coverage pytest
                    $VENV/bin/coverage run -m pytest
                    $VENV/bin/coverage html
                '''
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
            # Limpiar virtualenv al final
            sh 'rm -rf venv'
        }
    }
}