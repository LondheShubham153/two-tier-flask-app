pipeline {
    agent  none
    
    stages{
        stage("Code"){
		
		agent {
                label 'dev-server'
            }

            steps{
                git url: "https://github.com/rohit808077/two-tier-flask-app.git", branch: "master"
            }
        }
        
    }
}
