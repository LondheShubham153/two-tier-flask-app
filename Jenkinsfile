pipeline {
    
    agent {label "dev"};
    
    stages {
        stage('code clone'){
            steps{
                git url:'https://github.com/jkabirqa/two-tier-flask-app.git', branch:'master'
            }
        }
        stage('build'){
            steps{
                sh 'docker build -t twotapp .'
            }
        }
        stage('test'){
            steps{
                echo 'testing testing hello'
            }
        }
        stage('push to docker hub') {
           steps {
               // script{
               //     docker_push("dockerHubCreds", "twotapp")
               withCredentials([usernamePassword(
                   credentialsId: "dhcredsforJenkins",
                   passwordVariable: "dockerHubPass",
                   usernameVariable: "dockerHubUser"
                )]) {
                   sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                   sh "docker image tag twotapp ${env.dockerHubUser}/twotapp"
                   sh "docker push ${env.dockerHubUser}/twotapp:latest"
                }
           
           }
           
        }   
         stage('deploy'){
            steps{
                sh "docker compose up -d --build twotapp"
            }
            
        }
    }

post{
        success{
            script{
                emailext from: 'jkabirq@gmail.com',
                to: 'jkabirm@gmail.com',
                body: 'Build success for Demo CICD App',
                subject: 'Build success for Demo CICD App'
            }
        }
        failure{
            script{
                emailext from: 'jkabirq@gmail.com',
                to: 'jkabirm@gmail.com',
                body: 'Build Failed for Demo CICD App',
                subject: 'Build Failed for Demo CICD App'
            }
        }
    }
}
    
