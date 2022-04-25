aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 590503010210.dkr.ecr.us-east-1.amazonaws.com
docker build -t android-cicd .
docker tag android-cicd:latest 590503010210.dkr.ecr.us-east-1.amazonaws.com/android-cicd:latest
docker push 590503010210.dkr.ecr.us-east-1.amazonaws.com/android-cicd:latest