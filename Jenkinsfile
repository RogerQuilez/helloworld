pipeline {
    agent any

    options { skipDefaultCheckout() }

     stages {
        stage('Get Code') {
            steps {
                git 'https://github.com/RogerQuilez/helloworld.git'
	            echo WORKSPACE
                bat 'dir'
                stash name:'code', includes:'**'
            }
        }

        stage('Build') {
           steps {
              echo 'Eyyy, esto es Python. No hay que compilar nada!!!'
           }
        }

        stage('Tests')
        {
            parallel
            {
                stage('Unit') {
                    agent {label 'agent1'}
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            sh '''
                                ls -la
                                export PYTHONPATH=${WORKSPACE}
                                /home/agent1/.local/bin/pytest --junitxml=result-unit.xml test/unit
                            '''
                            stash name:'unit-res', includes:'result-unit.xml'
                       }
                    }
                }


                stage('Rest') {
                    agent {label 'agent1'}
                    steps {
                      catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        unstash name:'code'
                        sh '''
                            export FLASK_APP=app/api.py
                            /home/agent2/.local/bin/flask run &

                            sleep 4

                            java -jar /home/agent2/wiremock/wiremock-standalone-3.3.1.jar --port 9090 --root-dir /home/agent2/wiremock &
                            export PYTHONPATH=${WORKSPACE}

                            sleep 15

                            /home/agent2/.local/bin/pytest --junitxml=result-rest.xml test/rest
                        '''
                      }
                      stash name:'rest-res', includes:'result-rest.xml'
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