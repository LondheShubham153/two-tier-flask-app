pipeline {
    agent  { label 'dev-server' }
    
    stages{
        stage("Code"){
            steps{
                git url: "https://github.com/rohit808077/two-tier-flask-app.git", branch: "master"
            }
        }
        stage("Build & Test"){
            steps{
                sh "docker build -t two-tier-falsk-app ."
            }
        }
        stage("Push to DockerHub"){
            steps{
                withCredentials([usernamePassword(credentialsId:"dockerHub",passwordVariable:"dockerHubPass",usernameVariable:"dockerHubUser")]){
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker tag two-tier-falsk-app ${env.dockerHubUser}/two-tier-falsk-app"
                    sh "docker push ${env.dockerHubUser}/two-tier-falsk-app" 
                }
            }
        }
        stage("Deploy"){
            steps{
                sh "docker-compose down && docker-compose up -d"
            }
        }
    }
}
