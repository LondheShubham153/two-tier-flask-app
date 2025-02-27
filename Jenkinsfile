pipeline {
    
    agent any;
    
    stages {
        stage('code clone'){
            steps{
                git url:'https://github.com/LondheShubham153/two-tier-flask-app.git', branch:'master'
            }
        }
        stage('build'){
            steps{
                sh 'docker build -t twotapp .'
            }
        }
        stage('test'){
            steps{
                echo 'testing'
            }
        }
        stage('push to docker hub') {
           steps {
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
                sh 'docker compose up -d --build flask-app'
            }
            
        }
    }

}










// #@Library("Shared") _
// pipeline{
    
// #    agent { label "dev"};
//      agent any;
//     stages{
//         stage("Code Clone"){
//             steps{
//                script{
//                    clone("https://github.com/LondheShubham153/two-tier-flask-app.git", "master")
//                }
//             }
//         }
//         stage("Trivy File System Scan"){
//             steps{
//                 script{
//                     trivy_fs()
//                 }
//             }
//         }
//         stage("Build"){
//             steps{
//                 sh "docker build -t two-tier-flask-app ."
//             }
            
//         }
//         stage("Test"){
//             steps{
//                 echo "Developer / Tester tests likh ke dega..."
//             }
            
//         }
//         stage("Push to Docker Hub"){
//             steps{
//                 script{
//                     docker_push("dockerHubCreds","two-tier-flask-app")
//                 }  
//             }
//         }
//         stage("Deploy"){
//             steps{
//                 sh "docker compose up -d --build flask-app"
//             }
//         }
//     }

// post{
//         success{
//             script{
//                 emailext from: 'mentor@trainwithshubham.com',
//                 to: 'mentor@trainwithshubham.com',
//                 body: 'Build success for Demo CICD App',
//                 subject: 'Build success for Demo CICD App'
//             }
//         }
//         failure{
//             script{
//                 emailext from: 'mentor@trainwithshubham.com',
//                 to: 'mentor@trainwithshubham.com',
//                 body: 'Build Failed for Demo CICD App',
//                 subject: 'Build Failed for Demo CICD App'
//             }
//         }
//     }
// }










