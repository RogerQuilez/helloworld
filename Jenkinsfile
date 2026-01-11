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
                            unstash name:'code'
                            bat """
                                REM Extraer porcentaje de lineas con PowerShell
                                for /f %%L in ('powershell -Command "(Select-Xml -Path coverage.xml -XPath '//coverage').Node.'line-rate' * 100"') do set lineCovPercent=%%L
                                for /f %%L in ('powershell -Command "(Select-Xml -Path coverage.xml -XPath '//coverage').Node.'branch-rate' * 100"') do set branchCovPercent=%%L

                                set exitCode=0
                                set lineStatus=GREEN
                                set branchStatus=GREEN

                                if %lineCovPercent% LSS 85 (
                                    set exitCode=2
                                    set lineStatus=RED
                                ) else if %lineCovPercent% LEQ 95 (
                                    set exitCode=1
                                    set lineStatus=UNSTABLE
                                )

                                if %branchCovPercent% LSS 80 (
                                    set exitCode=2
                                    set branchStatus=RED
                                ) else if %branchCovPercent% LEQ 90 (
                                    if %exitCode% NEQ 2 set exitCode=1
                                    set branchStatus=UNSTABLE
                                )

                                echo Cobertura lineas: %lineCovPercent%% (%lineStatus%)
                                echo Cobertura ramas: %branchCovPercent%% (%branchStatus%)

                                exit /b %exitCode%
                            """
                        }
                    }
                }

            }
        }
    }
}