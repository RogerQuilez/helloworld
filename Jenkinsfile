pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    stages {

        stage('Get Code') {
            agent { label 'master' }
            steps {
                checkout scm
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
                            dir
                            set PYTHONPATH=%WORKSPACE%
                            C:\\Python311\\Scripts\\pytest.exe --junitxml=result-unit.xml --cov=app --cov-report=xml test\\unit || exit /b 0
                        """
                        stash name:'unit-res', includes:'result-unit.xml'
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
                            set PYTHONPATH=%WORKSPACE%
                            ping 127.0.0.1 -n 16 > nul
                            C:\\Python311\\Scripts\\pytest.exe --junitxml=result-rest.xml test\\rest || exit /b 0
                        """
                        stash name:'rest-res', includes:'result-rest.xml'
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
                                echo \$xml = [xml](Get-Content 'coverage.xml') > check_coverage.ps1
                                echo \$cov = \$xml.SelectSingleNode('//coverage') >> check_coverage.ps1
                                echo \$lineRate = [double](\$cov.GetAttribute('line-rate')) >> check_coverage.ps1
                                echo \$branchRate = [double](\$cov.GetAttribute('branch-rate')) >> check_coverage.ps1
                                echo \$line = [math]::Round((\$lineRate * 100),0) >> check_coverage.ps1
                                echo \$branch = [math]::Round((\$branchRate * 100),0) >> check_coverage.ps1
                                echo \$exitCode = 0 >> check_coverage.ps1
                                echo if (\$line -lt 85 -or \$branch -lt 80) { \$exitCode = 2 } elseif (\$line -le 95 -or \$branch -le 90) { \$exitCode = 1 } >> check_coverage.ps1
                                echo exit \$exitCode >> check_coverage.ps1
                                powershell -NoProfile -ExecutionPolicy Bypass -File check_coverage.ps1
                                del check_coverage.ps1
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
                                if not exist test\\performance mkdir test\\performance
                                set FLASK_APP=app\\api.py
                                start /B C:\\Python311\\Scripts\\flask.exe run
                                ping 127.0.0.1 -n 10 > nul
                                C:\\apache-jmeter-5.6.3\\bin\\jmeter.bat -n -t test\\jmeter\\flask.jmx -l test\\performance\\result-performance.jtl
                                C:\\apache-jmeter-5.6.3\\bin\\JMeterPluginsCMD.bat --generate-png test\\performance\\performance.png --input-jtl test\\performance\\result-performance.jtl --plugin-type AggregateReport
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
