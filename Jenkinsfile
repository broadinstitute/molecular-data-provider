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
    environment {
        TRANSFORMERS = "ctrp"
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
                        changeset "**"
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
                        changeset "**"
                        triggeredBy 'UserIdCause'
                    }
                }
            }
            steps {
                withEnv([
                    "IMAGE_NAME=853771734544.dkr.ecr.us-east-1.amazonaws.com/translator-molepro-ctrp",
                    "BUILD_VERSION=" + (params.BUILD_VERSION ?: env.BUILD_VERSION)
                ]) {
                    script {
                        docker.build("${env.IMAGE_NAME}", "--build-arg SOURCE_FOLDER=./${BUILD_VERSION} --no-cache .")
                        sh '''
                        docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 853771734544.dkr.ecr.us-east-1.amazonaws.com
                        '''
                        docker.image("${env.IMAGE_NAME}").push("${BUILD_VERSION}")
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    changeset "**"
                    triggeredBy 'UserIdCause'
                }
            }
            agent {
                label 'translator && ci && deploy'
            }
            steps {
                configFileProvider([
                    configFile(fileId: 'values-transformers.yaml', targetLocation: 'values-transformers.yaml'),
                    configFile(fileId: 'prepare.sh', targetLocation: 'prepare.sh')
                ]){
                    script {
                        sh '''
                        aws --region ${AWS_REGION} eks update-kubeconfig --name ${KUBERNETES_CLUSTER_NAME}
                        /bin/bash prepare.sh
                        cp translator-ops/ops/molepro/config/transformers/molepro-ctrp.yaml translator-ops/ops/molepro/helm/
                        cd translator-ops/ops/molepro/helm/
                        /bin/bash deploy.sh
                        '''
                    } 
                }    
            }
            post {
                always {
                    echo " Clean up the workspace in deploy node!"
                    cleanWs()
                }
            }
        }
    }
}