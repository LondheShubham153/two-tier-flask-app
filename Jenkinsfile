pipeline{
    
    agent { label "dev" };
    
    stages{
        stage("Code Clone"){
            steps{
                git url: "https://github.com/Yajat541/two-tier-flask-app.git",branch: "master"
            }
        }
        stage("Build"){
            steps{
                sh "docker build -t two-tier-flask-app ."
            }
        }
        stage("Test"){
            steps{
                echo "Tester tests likh kardega"
            }
        }
        stage("Push to Docker Hub"){
            steps{
                withCredentials([usernamePassword(
                    credentialsId: "dockerhubCreds",
                    passwordVariable: "dockerHubPass",
                    usernameVariable: "dockerHubUser"
                )]){
                        
                sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                sh "docker image tag two-tier-flask-app ${env.dockerHubUser}/two-tier-flask-app"
                sh "docker push ${env.dockerHubUser}/two-tier-flask-app:latest"
            }
            }
        }
        stage("Deploy"){
            steps{
            sh "docker compose down --remove-orphans || true"
            sh "docker rm -f mysql flask-app || true"
            sh "docker compose up -d --build"
            }
        }
    }
    
}
