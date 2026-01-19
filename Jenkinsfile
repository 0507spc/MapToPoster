pipeline {
  agent { label 'miniserver' }

  environment {
    REGISTRY_URL   = 'nexus.server.cranie.com/docker'
    REGISTRY_REPO  = 'maptoposter'          // nexus.server.cranie.com/maptoposter/...
    IMAGE_NAME     = 'maptoposter-api'

    REGISTRY_CREDS = 'nexus-docker-creds'
  }

  options {
    timestamps()
  }

  triggers {
    // Example: daily at 02:00; tune as you like
    cron('H 2 * * *')
  }

  stages {

    stage('Checkout pipeline repo') {
      steps {
        checkout scm
      }
    }

    stage('Compute image tag') {
      steps {
        script {
          def gitHash = sh(
            script: 'git rev-parse --short HEAD',
            returnStdout: true
          ).trim()
          env.FULL_TAG     = "${gitHash}-${env.BUILD_NUMBER}"
          env.DOCKER_IMAGE = "${REGISTRY_URL}/${REGISTRY_REPO}/${IMAGE_NAME}:${FULL_TAG}"
          env.LATEST_IMAGE = "${REGISTRY_URL}/${REGISTRY_REPO}/${IMAGE_NAME}:latest"
        }
        echo "Image: ${env.DOCKER_IMAGE}"
        echo "Latest: ${env.LATEST_IMAGE}"
      }
    }

    stage('Docker Build') {
      steps {
        dir('api') {
          sh '''
            docker build \
              -t "${IMAGE_NAME}:${FULL_TAG}" \
              .
          '''
        }
      }
    }

    stage('Tag for Nexus') {
      steps {
        sh '''
          docker tag "${IMAGE_NAME}:${FULL_TAG}" "${DOCKER_IMAGE}"
          docker tag "${IMAGE_NAME}:${FULL_TAG}" "${LATEST_IMAGE}"
        '''
      }
    }

    stage('Login to Nexus') {
      steps {
        withCredentials([usernamePassword(credentialsId: REGISTRY_CREDS,
                                          usernameVariable: 'NEXUS_USER',
                                          passwordVariable: 'NEXUS_PASS')]) {
          sh '''
            echo "${NEXUS_PASS}" | docker login "${REGISTRY_URL}" \
              --username "${NEXUS_USER}" --password-stdin
          '''
        }
      }
    }

    stage('Push to Nexus') {
      steps {
        sh '''
          docker push "${DOCKER_IMAGE}"
          docker push "${LATEST_IMAGE}"
        '''
      }
    }
  }

  post {
    always {
      sh 'docker logout "${REGISTRY_URL}" || true'
      sh 'docker image prune -f || true'
    }
  }
}
