pipeline {
    agent none

    options {
        skipDefaultCheckout()
    }

    stages {

        stage('Get Code') {
            agent { label 'master' }
            steps {
                git 'https://github.com/RogerQuilez/helloworld.git'
                echo "WORKSPACE = ${env.WORKSPACE}"
                bat 'dir'
                stash name: 'code', includes: '**'
            }
        }

        stage('Tests') {
            parallel {

                stage('Unit') {
                    agent { label 'python-test' }
                    steps {
                        unstash 'code'
                        bat """
                            set PYTHONPATH=%WORKSPACE%
                            C:\\Python311\\Scripts\\pytest.exe --junitxml=result-unit.xml --cov=app --cov-report=xml test\\unit || exit /b 0
                        """
                        stash name: 'unit-res', includes: 'result-unit.xml'
                    }
                }

                stage('Rest') {
                    agent { label 'python-test' }
                    steps {
                        unstash 'code'
                        bat """
                            set FLASK_APP=app\\api.py
                            start /B C:\\Python311\\Scripts\\flask.exe run
                            ping 127.0.0.1 -n 16 > nul

                            start /B java -jar C:\\Users\\rogerqp\\wiremock\\wiremock-standalone-3.13.2.jar --port 9090 --root-dir "%WORKSPACE%\\test\\wiremock"
                            ping 127.0.0.1 -n 16 > nul

                            set PYTHONPATH=%WORKSPACE%
                            C:\\Python311\\Scripts\\pytest.exe --junitxml=result-rest.xml test\\rest || exit /b 0
                        """
                        stash name: 'rest-res', includes: 'result-rest.xml'
                    }
                }

                stage('Static') {
                    agent { label 'python-test' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash 'code'
                            bat """
                                C:\\Python311\\Scripts\\flake8.exe app test > flake8_report.txt 2>&1
                                for /F %%L in ('type flake8_report.txt ^| find /C ":"') do set count=%%L

                                if %count% GEQ 10 (exit /b 2)
                                if %count% GEQ 8 (exit /b 1)
                                exit /b 0
                            """
                        }
                    }
                }

                stage('Security') {
                    agent { label 'python-test' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash 'code'
                            bat """
                                C:\\Python311\\Scripts\\bandit.exe -r app test -f txt -o bandit_report.txt
                                for /F %%L in ('type bandit_report.txt ^| find /C "Issue:"') do set count=%%L

                                if %count% GEQ 4 (exit /b 2)
                                if %count% GEQ 2 (exit /b 1)
                                exit /b 0
                            """
                        }
                    }
                }

                stage('Coverage') {
                    agent { label 'python-test' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash 'code'
                            bat """
                                powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                                "$xml=[xml](Get-Content 'coverage.xml'); ^
                                 $cov=$xml.coverage; ^
                                 $line=[math]::Round($cov.'line-rate'*100,0); ^
                                 $branch=[math]::Round($cov.'branch-rate'*100,0); ^
                                 if ($line -lt 85 -or $branch -lt 80) { exit 2 } ^
                                 elseif ($line -le 95 -or $branch -le 90) { exit 1 } ^
                                 else { exit 0 }"
                            """
                        }
                    }
                }

                stage('Performance') {
                    agent { label 'performance' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash 'code'
                            bat """
                                set FLASK_APP=app\\api.py
                                start /B C:\\Python311\\Scripts\\flask.exe run
                                ping 127.0.0.1 -n 10 > nul

                                C:\\apache-jmeter-5.6.3\\bin\\jmeter.bat -n ^
                                  -t test\\jmeter\\flask.jmx ^
                                  -l test\\performance\\result-performance.jtl

                                C:\\apache-jmeter-5.6.3\\bin\\JMeterPluginsCMD.bat ^
                                  --generate-png test\\performance\\performance.png ^
                                  --input-jtl test\\performance\\result-performance.jtl ^
                                  --plugin-type AggregateReport
                            """
                        }
                    }
                    post {
                        always {
                            publishHTML(target: [
                                reportDir: 'test\\performance',
                                reportFiles: 'performance.png',
                                reportName: 'Performance Report'
                            ])
                        }
                    }
                }

            }
        }
    }
}