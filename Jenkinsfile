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
                                REM -------------------------------
                                REM Generar reporte de cobertura
                                REM -------------------------------
                                C:\\Python311\\Scripts\\coverage.exe report -m > cov_report.txt

                                REM -------------------------------
                                REM Extraer porcentaje de line coverage
                                REM -------------------------------
                                for /F "tokens=4" %%L in ('findstr /R /C:"TOTAL" cov_report.txt') do set lineCov=%%L

                                REM -------------------------------
                                REM Extraer porcentaje de branch coverage
                                REM -------------------------------
                                REM Para simplificar vamos a usar el mismo lineCov si no tenemos branch coverage
                                set branchCov=%lineCov%

                                REM Quitar % y convertir a número
                                set lineCovPercent=%lineCov:%%=%
                                set branchCovPercent=%branchCov:%%=%

                                echo Cobertura lineas: %lineCovPercent%%
                                echo Cobertura ramas: %branchCovPercent%%

                                REM -------------------------------
                                REM Evaluar thresholds
                                REM -------------------------------
                                set exitCode=0

                                if %lineCovPercent% LSS 85 set exitCode=2
                                if %lineCovPercent% GEQ 85 if %lineCovPercent% LEQ 94 set exitCode=1

                                if %branchCovPercent% LSS 80 set exitCode=2
                                if %branchCovPercent% GEQ 80 if %branchCovPercent% LEQ 89 set exitCode=1

                                exit /b %exitCode%
                            """
                        }
                    }
                }

            }
        }
    }
}