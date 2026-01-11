pipeline {
    agent any

    options { skipDefaultCheckout() }

    stages {
        stage('Get Code') {
            steps {
                git 'https://github.com/RogerQuilez/helloworld.git'
                echo "WORKSPACE = ${env.WORKSPACE}"
                bat 'dir'
                stash name:'code', includes:'**'
            }
        }

        stage('Build') {
            steps {
                echo 'Eyyy, esto es Python. No hay que compilar nada!!!'
            }
        }

        stage('Tests') {
            parallel {
                stage('Unit') {
                    agent { label 'windows-agent' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            bat """
                                dir
                                set PYTHONPATH=%WORKSPACE%
                                C:\\Python311\\Scripts\\pytest.exe --junitxml=result-unit.xml test\\unit
                            """
                            stash name:'unit-res', includes:'result-unit.xml'
                        }
                    }
                }

                stage('Rest') {
                    agent { label 'windows-agent' } // en realidad es Windows
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            bat """
                                set FLASK_APP=app\\api.py
                                start /B C:\\Python311\\Scripts\\flask.exe run

                                timeout /t 4

                                start /B java -jar C:\\Users\\rogerqp\\wiremock\\wiremock-standalone-3.13.2.jar --port 9090 --root-dir "%WORKSPACE%\\test\\wiremock"


                                set PYTHONPATH=%WORKSPACE%
                                ping 127.0.0.1 -n 40 > nul

                                C:\\Python311\\Scripts\\pytest.exe --junitxml=result-rest.xml test\\rest
                            """
                            stash name:'rest-res', includes:'result-rest.xml'
                        }
                    }
                }
            }
        }

        stage('Results') {
            steps {
                unstash name:'unit-res'
                unstash name:'rest-res'
                junit 'result*.xml'
            }
        }
    }
}