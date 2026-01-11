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
                    agent { label 'windows-agent' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            bat """
                                set FLASK_APP=app\\api.py
                                start /B C:\\Python311\\Scripts\\flask.exe run
                                ping 127.0.0.1 -n 16 > nul
                                start /B java -jar C:\\Users\\rogerqp\\wiremock\\wiremock-standalone-3.13.2.jar --port 9090 --root-dir "%WORKSPACE%\\test\\wiremock"
                                set PYTHONPATH=%WORKSPACE%
                                ping 127.0.0.1 -n 16 > nul
                                C:\\Python311\\Scripts\\pytest.exe --junitxml=result-rest.xml test\\rest
                            """
                            stash name:'rest-res', includes:'result-rest.xml'
                        }
                    }
                }

                stage('Static') {
                    agent { label 'windows-agent' }
                    steps {
                        unstash name:'code'
                        bat """
                            REM Ejecutar flake8 y guardar la salida en un archivo temporal
                            C:\\Python311\\Scripts\\flake8.exe app test > flake8_report.txt 2>&1
                            set /A count=0
                            for /F %%L in ('type flake8_report.txt ^| find /C ":"') do set count=%%L
                            echo Number of flake8 issues: %count%

                            REM Evaluar resultados
                            if %count% GEQ 10 (
                                echo Found 10 or more issues -> Marking build as FAILURE
                                exit /b 2
                            ) else if %count% GEQ 8 (
                                echo Found 8 or more issues -> Marking build as UNSTABLE
                                exit /b 1
                            ) else (
                                echo Less than 8 issues -> Build OK
                                exit /b 0
                            )
                        """
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