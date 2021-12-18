pipeline {
    options {
        timestamps()
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }
    agent {
        node { label 'translator && aws && build' }
    }
    parameters {
        string(name: 'BUILD_VERSION', defaultValue: '', description: 'The build version to deploy (optional)')
        string(name: 'AWS_REGION', defaultValue: 'us-east-1', description: 'AWS Region to deploy')
        string(name: 'KUBERNETES_CLUSTER_NAME', defaultValue: 'translator-eks-ci-blue-cluster', description: 'AWS EKS that will host this application')
    }
    triggers {
        pollSCM('H/2 * * * *')
    }
    stages {
        stage('Clean') {
            steps {
                cleanWs()
                checkout scm
            }
        }
        stage('Build Version') {
            when {
                allOf {
                    expression {
                        return !params.BUILD_VERSION
                    }
                    anyOf {
                        changeset "*"
                        triggeredBy 'UserIdCause'
                    }
                }
            }
            steps{
               script {
                    BUILD_VERSION_GENERATED = VersionNumber(
                        versionNumberString: 'v${BUILD_YEAR, XX}.${BUILD_MONTH, XX}${BUILD_DAY, XX}.${BUILDS_TODAY}',
                        skipFailedBuilds:    true)
                    currentBuild.displayName = BUILD_VERSION_GENERATED
                    env.BUILD_VERSION = BUILD_VERSION_GENERATED
              }
           }
        }
        stage('build') {
            when {
                allOf {
                    expression {
                        return !params.BUILD_VERSION
                    }
                    anyOf {
                        changeset "*"
                        triggeredBy 'UserIdCause'
                    }
                }
            }
            steps {
                withEnv([
                    "IMAGE_NAME=translator-molepro-molepro",
                    "BUILD_VERSION=" + (params.BUILD_VERSION ?: env.BUILD_VERSION)
                ]) {
                    dir(".") {
                        script {
                             docker.build("${env.IMAGE_NAME}", "--build-arg SOURCE_FOLDER=./${BUILD_VERSION} --no-cache .")
                                 docker.withRegistry('https://853771734544.dkr.ecr.us-east-1.amazonaws.com', 'ecr:us-east-1:ifx-jenkins-ci') {
                                     docker.image("${env.IMAGE_NAME}").push("${BUILD_VERSION}")
                            }
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            when {
                anyOf {
                    changeset "*"
                    triggeredBy 'UserIdCause'
                }
            }
            steps {
                sshagent (credentials: ['0360ecc2-120b-49df-ad82-a1c53fa961d0']) {
                    dir(".") {
                        sh 'git clone git@github.com:Sphinx-Automation/translator-ops.git'
                        configFileProvider([
                            configFile(fileId: 'molepro-api-ci-env', targetLocation: 'translator-ops/ops/molepro/moleproapi/.env')
                        ]){
                            withAWS(credentials:'aws-ifx-deploy') {
                                sh '''
                                aws --region ${AWS_REGION} eks update-kubeconfig --name ${KUBERNETES_CLUSTER_NAME}
                                cd translator-ops/ops/molepro/moleproapi/
                                /bin/bash deploy.sh
                                '''
                            }
                        }
                    }
                }
            }
        }
    }
}
