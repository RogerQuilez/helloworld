pipeline {
    agent any

    environment {
        VENV = "venv"
        JMETER_HOME = "/opt/jmeter"
    }

    stages {

        stage('Unit') {
            steps {
                sh '''
                    python3 -m venv $VENV
                    . $VENV/bin/activate
                    pip install --upgrade pip
                    pip install pytest
                    pytest test/unit --junitxml=unit-results.xml
                '''
            }
            post {
                always {
                    junit 'unit-results.xml'
                }
            }
        }

        stage('Rest') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    pip install pytest requests
                    pytest test/rest --junitxml=rest-results.xml
                '''
            }
            post {
                always {
                    junit 'rest-results.xml'
                }
            }
        }

        stage('Static') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    pip install flake8
                    flake8 app
                '''
            }
        }

        stage('Security Test') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    pip install bandit
                    bandit -r app
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
                    . $VENV/bin/activate
                    pip install coverage pytest
                    coverage run -m pytest
                    coverage html
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
            sh 'rm -rf venv'
        }
    }
}
