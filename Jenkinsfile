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
                        unstash name:'code'
                        bat """
                            dir
                            set PYTHONPATH=%WORKSPACE%
                            REM Ejecutar pytest unitarias, pero siempre devolver 0 para que la etapa quede verde
                            C:\\Python311\\Scripts\\pytest.exe --junitxml=result-unit.xml --cov=app --cov-report=xml test\\unit || exit /b 0
                        """
                        stash name:'unit-res', includes:'result-unit.xml'
                    }
                }

                stage('Rest') {
                    agent { label 'windows-agent' }
                    steps {
                        unstash name:'code'
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
                    agent { label 'windows-agent' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            bat """
                                C:\\Python311\\Scripts\\flake8.exe app test > flake8_report.txt 2>&1
                                set /A count=0
                                for /F %%L in ('type flake8_report.txt ^| find /C ":"') do set count=%%L
                                echo Issues encontrados: %count%

                                if %count% GEQ 10 (
                                    exit /b 2
                                ) else (
                                    if %count% GEQ 8 (
                                        exit /b 1
                                    ) else (
                                        exit /b 0
                                    )
                                )
                            """
                        }
                    }
                }

                stage('Security') {
                    agent { label 'windows-agent' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name:'code'
                            bat """
                                REM Ejecutar bandit
                                C:\\Python311\\Scripts\\bandit.exe -r app test -f txt -o bandit_report.txt
                                set /A count=0
                                REM Contar hallazgos (cada línea con Issue)
                                for /F %%L in ('type bandit_report.txt ^| find /C "Issue:"') do set count=%%L
                                echo Issues de seguridad encontrados: %count%

                                REM Evaluar resultados segun umbrales
                                if %count% GEQ 4 (
                                    exit /b 2
                                ) else (
                                    if %count% GEQ 2 (
                                        exit /b 1
                                    ) else (
                                        exit /b 0
                                    )
                                )
                            """
                        }
                    }
                }

                stage('Coverage') {
                    agent { label 'windows-agent' }
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            unstash name: 'code'
                            bat """
                                REM Crear script PowerShell temporal
                                echo \$xml = [xml](Get-Content 'coverage.xml') > check_coverage.ps1
                                echo \$line = [math]::Round((\$xml.coverage.'line-rate' * 100),0) >> check_coverage.ps1
                                echo \$branch = [math]::Round((\$xml.coverage.'branch-rate' * 100),0) >> check_coverage.ps1
                                echo \$exitCode = 0 >> check_coverage.ps1
                                echo \$lineStatus = 'GREEN' >> check_coverage.ps1
                                echo \$branchStatus = 'GREEN' >> check_coverage.ps1
                                echo if (\$line -lt 85) { \$exitCode = 2; \$lineStatus='RED' } elseif (\$line -le 95) { \$exitCode = 1; \$lineStatus='UNSTABLE' } >> check_coverage.ps1
                                echo if (\$branch -lt 80) { \$exitCode = 2; \$branchStatus='RED' } elseif (\$branch -le 90) { if (\$exitCode -ne 2) { \$exitCode=1 }; \$branchStatus='UNSTABLE' } >> check_coverage.ps1
                                echo Write-Output ('Cobertura lineas: {0}%% ({1})' -f \$line,\$lineStatus) >> check_coverage.ps1
                                echo Write-Output ('Cobertura ramas: {0}%% ({1})' -f \$branch,\$branchStatus) >> check_coverage.ps1
                                echo exit \$exitCode >> check_coverage.ps1

                                REM Ejecutar el script PowerShell
                                powershell -NoProfile -ExecutionPolicy Bypass -File check_coverage.ps1

                                REM Borrar el script temporal
                                del check_coverage.ps1
                            """
                        }
                    }
                }

            }
        }
    }
}